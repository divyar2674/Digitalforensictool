from django.http import JsonResponse, HttpResponse
import csv
from datetime import datetime
import json
from django.utils import timezone

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

from .models import FileEvent, Investigator, Case, Evidence, ChainOfCustody, BrowserEvent, WindowsEvent

from Dataingestion.windowlogscollector import collect_windows_logs
from Dataingestion.filemetadatacollector import collect_files
from Dataingestion.browserdatacollector import (
    get_browser_paths,
    copy_db,
    extract_browser_data
)
from Dataingestion.Recyclebinfilecollector import collect_recycle_bin_files

from parser.recyclebin_parser import parse_recycle_bin_file

from normalizer import (
    normalize_windows_events,
    normalize_file_events,
    normalize_browser_events,
    normalize_recycle_events
)

from Timeline import build_timeline

from aihelper.collector import collect_all_events
from aihelper.timeframe import build_timeframes
from aihelper.rules import analyze_timeframes
from aihelper.predictor import generate_predictions
from aihelper.summary import generate_summary

from django.views.decorators.csrf import csrf_exempt

import os
import re


# =========================
# START INVESTIGATION
# =========================
@csrf_exempt
def start_investigation(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            investigator = Investigator.objects.create(
                name=data.get("name"),
                badge_id=data.get("badge_id"),
                role=data.get("role")
            )

            case = Case.objects.create(
                case_id=data.get("case_id"),
                title=data.get("title"),
                description=data.get("description"),
                investigator=investigator
            )

            evidence = Evidence.objects.create(
                case=case,
                device_name=data.get("device_name"),
                path=data.get("path")
            )

            ChainOfCustody.objects.create(
                evidence=evidence,
                investigator=investigator,
                action="COLLECTED",
                notes=f"Device {evidence.device_name} registered"
            )

            return JsonResponse({
                "message": "Investigation started",
                "case_id": case.case_id,
                "investigator": investigator.name
            })

        except Exception as e:
            print("[ERROR] Start Investigation:", str(e))
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "POST required"}, status=400)


# =========================
# AI PIPELINE
# =========================
def run_ai_pipeline(timeline):
    try:
        timeframes = build_timeframes(timeline)
        alerts = analyze_timeframes(timeframes)
        predictions = generate_predictions(timeframes, alerts)
        summary = generate_summary(timeline, alerts, predictions)
        return alerts, predictions, summary
    except Exception as e:
        print("[ERROR] AI failed:", e)
        return [], [], {"overview": "AI failed"}


# =========================
# FILTER 2026
# =========================
def filter_2026(events):
    filtered = []
    for e in events:
        ts = e.get("timestamp")
        try:
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            if ts and ts.year == 2026:
                e["timestamp"] = ts
                filtered.append(e)
        except:
            continue
    return filtered


# =========================
# REMOVE DUPLICATES
# =========================
def remove_duplicates(events):
    seen = set()
    unique = []

    for e in events:
        key = (
            str(e.get("timestamp")),
            e.get("event_type"),
            e.get("file_name"),
            e.get("source"),
            e.get("details")
        )
        if key not in seen:
            seen.add(key)
            unique.append(e)

    return unique


# =========================
# CLEAN PATH
# =========================
def clean_path(p):
    if not p:
        return None

    match = re.search(r"[a-zA-Z]:\\.*", p)
    if match:
        p = match.group(0)

    return os.path.normcase(os.path.normpath(p))


# =========================
# ENRICH DELETED EVENTS
# =========================
def enrich_deleted_events(events, case):
    enriched = []

    for e in events:
        if e.get("event_type") == "FILE_DELETED":
            try:
                raw_path = e.get("details")
                path = clean_path(raw_path)

                if not path:
                    enriched.append(e)
                    continue

                file_name = os.path.basename(path)

                candidates = FileEvent.objects.filter(
                    case=case,
                    file_name__iexact=file_name,
                    timestamp__lt=e.get("timestamp")
                ).order_by("timestamp")

                created = modified = accessed = None

                for r in candidates:
                    if r.event_type == "FILE_CREATED" and not created:
                        created = r.timestamp
                    elif r.event_type == "FILE_MODIFIED":
                        modified = r.timestamp
                    elif r.event_type == "FILE_ACCESSED":
                        accessed = r.timestamp

                if created or modified or accessed:
                    e.setdefault("metadata", {})
                    e["metadata"]["previous_state"] = {
                        "created_time": str(created) if created else None,
                        "modified_time": str(modified) if modified else None,
                        "accessed_time": str(accessed) if accessed else None,
                    }

            except Exception as err:
                print("[ERROR] Enrich failed:", err)

        enriched.append(e)

    return enriched


# =========================
# TIMELINE API
# =========================
def get_timeline_data(request):

    case_id = request.GET.get("case_id")

    if not case_id:
        return JsonResponse({"error": "Enter investigator details first"}, status=400)

    try:
        case = Case.objects.get(case_id=case_id)
    except Case.DoesNotExist:
        return JsonResponse({"error": "Invalid case"}, status=404)

    evidence = Evidence.objects.filter(case=case).first()
    investigator = case.investigator

    ChainOfCustody.objects.create(
        evidence=evidence,
        investigator=investigator,
        action="SCAN_STARTED",
        notes="Scan initiated"
    )

    all_events = []

    try:
        scan_path = evidence.path if evidence and evidence.path else "C:\\"

        if not os.path.exists(scan_path):
            return JsonResponse({"error": f"Invalid path: {scan_path}"}, status=400)

        print(f"[INFO] Scanning path: {scan_path}")

        all_events += normalize_windows_events(collect_windows_logs(500), case=case)
        all_events += normalize_file_events(collect_files(scan_path, 500), case=case)

        for name, path in get_browser_paths().items():
            db = copy_db(path, name)
            if db:
                all_events += normalize_browser_events(
                    extract_browser_data(db, name),
                    case=case
                )

        drive = scan_path.split("\\")[0] + "\\"
        recycle_files = collect_recycle_bin_files(drive + "$Recycle.Bin")

        parsed = []
        for f in recycle_files:
            result = parse_recycle_bin_file(f)
            if result:
                parsed.append(result)

        all_events += normalize_recycle_events(parsed, case=case)

    except Exception as e:
        print("[ERROR] Pipeline failed:", str(e))
        return JsonResponse({"error": str(e)}, status=500)

    # FILTER + CLEAN
    all_events = remove_duplicates(filter_2026(all_events))

    fixed_events = []
    for e in all_events:
        ts = e.get("timestamp")

        if not ts:
            continue

        try:
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)

            if timezone.is_naive(ts):
                ts = timezone.make_aware(ts)

            e["timestamp"] = ts
            fixed_events.append(e)

        except Exception as err:
            print("[ERROR] Timestamp fix:", err)

    fixed_events = enrich_deleted_events(fixed_events, case)

    timeline = build_timeline(fixed_events)

    alerts, predictions, summary = run_ai_pipeline(timeline)

    ChainOfCustody.objects.create(
        evidence=evidence,
        investigator=investigator,
        action="SCAN_COMPLETED",
        notes=f"{len(timeline)} events processed"
    )

    for e in timeline:
        e["timestamp"] = str(e["timestamp"])

    return JsonResponse({
        "case": case.case_id,
        "investigator": investigator.name,
        "timeline": timeline,
        "alerts": alerts,
        "predictions": predictions,
        "overview": summary.get("overview")
    }, safe=False)


# =========================
# SUMMARY
# =========================
def get_summary(request):
    timeline = collect_all_events()
    timeframes = build_timeframes(timeline)
    alerts = analyze_timeframes(timeframes)
    predictions = generate_predictions(timeframes, alerts)
    summary = generate_summary(timeline, alerts, predictions)
    return JsonResponse(summary, safe=False)


# =========================
# CSV EXPORT
# =========================
import csv
from django.http import HttpResponse


import csv
from django.http import HttpResponse


def export_csv(request):
    case_id = request.GET.get("case_id")

    case = Case.objects.filter(case_id=case_id).first()
    investigator = case.investigator if case else None
    evidence = Evidence.objects.filter(case=case).first()
    chain = ChainOfCustody.objects.filter(evidence=evidence)

    file_events = FileEvent.objects.filter(case=case)
    browser_events = BrowserEvent.objects.filter(case=case)
    windows_events = WindowsEvent.objects.filter(case=case)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="forensic_report.csv"'

    writer = csv.writer(response)

    # =========================
    # CASE INFO
    # =========================
    writer.writerow(["CASE INFORMATION"])
    writer.writerow(["Case ID", case.case_id if case else ""])
    writer.writerow(["Title", case.title if case else ""])
    writer.writerow(["Description", case.description if case else ""])
    writer.writerow(["Created At", case.created_at if case else ""])
    writer.writerow([])

    # =========================
    # INVESTIGATOR
    # =========================
    writer.writerow(["INVESTIGATOR DETAILS"])
    writer.writerow(["Name", investigator.name if investigator else ""])
    writer.writerow(["Badge ID", investigator.badge_id if investigator else ""])
    writer.writerow(["Role", investigator.role if investigator else ""])
    writer.writerow([])

    # =========================
    # EVIDENCE
    # =========================
    writer.writerow(["EVIDENCE DETAILS"])
    writer.writerow(["Device", evidence.device_name if evidence else ""])
    writer.writerow(["Path", evidence.path if evidence else ""])
    writer.writerow(["Hash", evidence.hash_value if evidence else ""])
    writer.writerow(["Collected At", evidence.collected_at if evidence else ""])
    writer.writerow([])

    # =========================
    # CHAIN OF CUSTODY
    # =========================
    writer.writerow(["CHAIN OF CUSTODY"])
    writer.writerow(["Timestamp", "Investigator", "Action", "Notes"])

    for c in chain:
        writer.writerow([
            c.timestamp,
            c.investigator.name,
            c.action,
            c.notes or ""
        ])

    writer.writerow([])

    # =========================
    # FILE EVENTS TABLE
    # =========================
    writer.writerow(["FILE EVENTS"])
    writer.writerow([
        "Timestamp", "Event Type", "Source", "File Name",
        "Path", "Size", "Extension",
        "Created", "Modified", "Accessed", "Deleted", "Note"
    ])

    for f in file_events:
        writer.writerow([
            f.timestamp,
            f.event_type,
            f.source,
            f.file_name,
            f.path,
            f.size,
            f.extension,
            f.created_time,
            f.modified_time,
            f.accessed_time,
            f.deleted_time,
            f.note
        ])

    writer.writerow([])

    # =========================
    # BROWSER EVENTS TABLE
    # =========================
    writer.writerow(["BROWSER EVENTS"])
    writer.writerow([
        "Timestamp", "Browser", "URL", "Title",
        "Visit Count", "Typed Count"
    ])

    for b in browser_events:
        writer.writerow([
            b.timestamp,
            b.browser,
            b.url,
            b.title,
            b.visit_count,
            b.typed_count
        ])

    writer.writerow([])

    # =========================
    # WINDOWS EVENTS TABLE
    # =========================
    writer.writerow(["WINDOWS EVENTS"])
    writer.writerow([
        "Timestamp", "Event Type", "Username",
        "IP Address", "Process", "Event ID", "Source"
    ])

    for w in windows_events:
        writer.writerow([
            w.timestamp,
            w.event_type,
            w.username,
            w.ip_address,
            w.process_name,
            w.event_id,
            w.source
        ])

    return response
# =========================
# PDF EXPORT
# =========================

from django.views.decorators.csrf import csrf_exempt
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.http import HttpResponse
from datetime import datetime
import json, base64
from io import BytesIO


@csrf_exempt
def export_pdf(request):
    data = json.loads(request.body)

    case_id = data.get("case_id")
    graph = data.get("graph")
    timeline = data.get("timeline", [])

    case = Case.objects.filter(case_id=case_id).first()
    investigator = case.investigator if case else None
    evidence = Evidence.objects.filter(case=case).first()
    chain = ChainOfCustody.objects.filter(evidence=evidence)

    file_events = FileEvent.objects.filter(case=case)
    browser_events = BrowserEvent.objects.filter(case=case)
    windows_events = WindowsEvent.objects.filter(case=case)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="forensic_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()

    wrap_style = ParagraphStyle(name='wrap', fontSize=9, leading=12)

    elements = []

    # =========================
    # TITLE
    # =========================
    elements.append(Paragraph("FORENSIC INVESTIGATION REPORT", styles['Title']))
    elements.append(Spacer(1, 20))

    # =========================
    # CASE INFO
    # =========================
    elements.append(Paragraph("<b>Case Information</b>", styles['Heading2']))
    elements.append(Spacer(1, 6))

    if case:
        elements.append(Paragraph(f"<b>Case ID:</b> {case.case_id}", styles['Normal']))
        elements.append(Paragraph(f"<b>Title:</b> {case.title}", styles['Normal']))
        elements.append(Paragraph(f"<b>Description:</b> {case.description}", styles['Normal']))
        elements.append(Paragraph(f"<b>Created At:</b> {case.created_at}", styles['Normal']))
        elements.append(Paragraph(
            f"<b>Generated On:</b> {datetime.now().strftime('%d %B %Y %H:%M')}",
            styles['Normal']
        ))

    elements.append(Spacer(1, 15))

    # =========================
    # INVESTIGATOR
    # =========================
    elements.append(Paragraph("<b>Investigator Details</b>", styles['Heading2']))

    if investigator:
        elements.append(Paragraph(f"Name: {investigator.name}", styles['Normal']))
        elements.append(Paragraph(f"Badge ID: {investigator.badge_id}", styles['Normal']))
        elements.append(Paragraph(f"Role: {investigator.role}", styles['Normal']))

    elements.append(Spacer(1, 15))

    # =========================
    # EVIDENCE
    # =========================
    elements.append(Paragraph("<b>Evidence Details</b>", styles['Heading2']))

    if evidence:
        elements.append(Paragraph(f"Device: {evidence.device_name}", styles['Normal']))
        elements.append(Paragraph(f"Path: {evidence.path}", styles['Normal']))
        elements.append(Paragraph(f"Hash: {evidence.hash_value}", styles['Normal']))
        elements.append(Paragraph(f"Collected At: {evidence.collected_at}", styles['Normal']))

    elements.append(Spacer(1, 15))

    # =========================
    # CHAIN OF CUSTODY
    # =========================
    elements.append(Paragraph("<b>Chain of Custody</b>", styles['Heading2']))

    for c in chain:
        elements.append(Paragraph(
            f"{c.timestamp} — {c.investigator.name} performed '{c.action}'. Notes: {c.notes or 'N/A'}",
            wrap_style
        ))

    elements.append(Spacer(1, 15))

    # =========================
    # GRAPH
    # =========================
    if graph:
        try:
            img_data = base64.b64decode(graph.split(",")[1])
            img = Image(BytesIO(img_data), width=450, height=220)

            elements.append(Paragraph("<b>Activity Overview</b>", styles['Heading2']))
            elements.append(img)
            elements.append(Spacer(1, 15))
        except:
            pass

    # =========================
    # TIMELINE
    # =========================
    elements.append(Paragraph("<b>Timeline of Events</b>", styles['Heading2']))

    for e in timeline:
        elements.append(Paragraph(
            f"{e['timestamp']} — {e['event_type']} — {e.get('file_name','')}",
            wrap_style
        ))

    elements.append(Spacer(1, 15))

    # =========================
    # FILE EVENTS
    # =========================
    elements.append(Paragraph("<b>File Activity</b>", styles['Heading2']))

    for f in file_events:
        elements.append(Paragraph(
            f"{f.timestamp} — {f.event_type} — {f.file_name} "
            f"(Path: {f.path}, Size: {f.size}, Note: {f.note or 'N/A'})",
            wrap_style
        ))

    elements.append(Spacer(1, 15))

    # =========================
    # BROWSER EVENTS
    # =========================
    elements.append(Paragraph("<b>Browser Activity</b>", styles['Heading2']))

    for b in browser_events:
        elements.append(Paragraph(
            f"{b.timestamp} — {b.browser} — {b.url} "
            f"(Title: {b.title or 'N/A'}, Visits: {b.visit_count})",
            wrap_style
        ))

    elements.append(Spacer(1, 15))

    # =========================
    # WINDOWS EVENTS
    # =========================
    elements.append(Paragraph("<b>System Events</b>", styles['Heading2']))

    for w in windows_events:
        elements.append(Paragraph(
            f"{w.timestamp} — {w.event_type} — User: {w.username or 'N/A'} "
            f"IP: {w.ip_address or 'N/A'} Process: {w.process_name or 'N/A'}",
            wrap_style
        ))

    doc.build(elements)
    return response

from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime


# 🔥 HEADER + FOOTER (BRANDING)
def add_header_footer(canvas, doc):
    canvas.saveState()

    # Header
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(40, 750, "Digital Forensics Lab")
    canvas.drawRightString(550, 750, "Confidential Report")

    # Footer
    canvas.setFont("Helvetica", 8)
    canvas.drawString(40, 30, "Generated by AI Forensic Analysis System")
    canvas.drawRightString(550, 30, f"Page {doc.page}")

    canvas.restoreState()



from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json


# =========================
# 🧠 MITRE MAPPING (FIXED)
# =========================
def map_mitre(alert):
    chain = alert.get("chain", "")
    if "FILE_DELETED" in chain:
        return "T1070 - Indicator Removal"
    elif "LOGIN_FAILED" in chain:
        return "T1110 - Brute Force"
    elif "BROWSER_VISIT" in chain:
        return "T1071 - Web Protocol"
    return "T1059 - Command Execution"


# =========================
# 📊 GRAPH FUNCTION (FIXED)
# =========================
def build_chart(alerts):
    high = sum(1 for a in alerts if a.get("risk") == "HIGH")
    med = sum(1 for a in alerts if a.get("risk") == "MEDIUM")
    low = sum(1 for a in alerts if a.get("risk") == "LOW")

    d = Drawing(200, 120)

    pie = Pie()
    pie.x = 50
    pie.y = 10
    pie.data = [high, med, low]
    pie.labels = ["HIGH", "MEDIUM", "LOW"]

    pie.slices[0].fillColor = colors.red
    pie.slices[1].fillColor = colors.orange
    pie.slices[2].fillColor = colors.green

    d.add(pie)
    return d


# =========================
# 📄 MAIN FUNCTION
# =========================
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json


# =========================
# 🧠 MITRE MAPPING
# =========================
def map_mitre(alert):
    chain = alert.get("chain", "")
    if "FILE_DELETED" in chain:
        return "T1070 - Indicator Removal"
    elif "LOGIN_FAILED" in chain:
        return "T1110 - Brute Force"
    elif "BROWSER_VISIT" in chain:
        return "T1071 - Web Protocol"
    return "T1059 - Command Execution"


# =========================
# 📊 GRAPH
# =========================
def build_chart(alerts):
    high = sum(1 for a in alerts if a.get("risk") == "HIGH")
    med = sum(1 for a in alerts if a.get("risk") == "MEDIUM")
    low = sum(1 for a in alerts if a.get("risk") == "LOW")

    d = Drawing(200, 120)

    pie = Pie()
    pie.x = 50
    pie.y = 10
    pie.data = [high, med, low]
    pie.labels = ["HIGH", "MEDIUM", "LOW"]

    pie.slices[0].fillColor = colors.red
    pie.slices[1].fillColor = colors.orange
    pie.slices[2].fillColor = colors.green

    d.add(pie)
    return d


# =========================
# 📄 MAIN FUNCTION
# =========================
@csrf_exempt
def export_summary_pdf(request):
    try:
        data = json.loads(request.body)

        case_id = data.get("case_id")
        alerts = data.get("alerts", [])

        case = Case.objects.filter(case_id=case_id).first() or Case.objects.order_by('-id').first()
        investigator = case.investigator if case else None
        events = FileEvent.objects.filter(case=case).order_by("timestamp")[:20] if case else []

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="forensic_report.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter)

        # =========================
        # STYLES
        # =========================
        title = ParagraphStyle(name="title", fontName="Times-Bold", fontSize=20, textColor=colors.darkblue, spaceAfter=10)
        section = ParagraphStyle(name="section", fontName="Times-Bold", fontSize=14, textColor=colors.darkblue, spaceAfter=6)
        normal = ParagraphStyle(name="normal", fontName="Times-Roman", fontSize=11, leading=14)
        small = ParagraphStyle(name="small", fontName="Times-Roman", fontSize=10, textColor=colors.grey)

        elements = []

        # =========================
        # TITLE
        # =========================
        elements.append(Paragraph("FORENSIC INCIDENT REPORT", title))

        # =========================
        # CASE OVERVIEW
        # =========================
        elements.append(Paragraph("Case Overview", section))

        case_table = Table([
            ["Case ID", getattr(case, "case_id", "N/A")],
            ["Title", getattr(case, "title", "N/A")],
            ["Investigator", getattr(investigator, "name", "N/A")],
        ], colWidths=[120, 300])

        case_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.lightblue),
            ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
            ('BOX', (0,0), (-1,-1), 1, colors.black)
        ]))

        elements.append(case_table)
        elements.append(Spacer(1, 15))

        # =========================
        # EXECUTIVE SUMMARY
        # =========================
        elements.append(Paragraph("Executive Summary", section))

        high = sum(1 for a in alerts if a.get("risk") == "HIGH")
        med = sum(1 for a in alerts if a.get("risk") == "MEDIUM")
        low = sum(1 for a in alerts if a.get("risk") == "LOW")

        elements.append(Paragraph(
            f"{len(alerts)} alerts detected (High: {high}, Medium: {med}, Low: {low}).",
            normal
        ))

        elements.append(Spacer(1, 15))

        # =========================
        # GRAPH
        # =========================
        elements.append(Paragraph("Alert Distribution", section))
        elements.append(build_chart(alerts))
        elements.append(Spacer(1, 15))

        # =========================
        # ALERT CARDS
        # =========================
        elements.append(Paragraph("Alert Analysis", section))

        for i, alert in enumerate(alerts, 1):

            risk = alert.get("risk", "LOW")
            bg = colors.red if risk == "HIGH" else colors.orange if risk == "MEDIUM" else colors.lightgreen

            alert_card = Table([
                [f"Alert {i} - {risk}"],
                [f"Explanation: {alert.get('explanation')}"],
                [f"MITRE: {map_mitre(alert)}"]
            ], colWidths=[420])

            alert_card.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), bg),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('BOX', (0,0), (-1,-1), 1, colors.black),
                ('INNERPADDING', (0,0), (-1,-1), 6)
            ]))

            elements.append(alert_card)
            elements.append(Spacer(1, 8))

            # EVENTS
            for e in alert.get("sequence", []):
                path = e.get("details") or e.get("file_path") or "N/A"

                elements.append(Paragraph(
                    f"• {e.get('timestamp')} → {e.get('event_type')}",
                    normal
                ))
                elements.append(Paragraph(path, small))

            elements.append(Spacer(1, 12))

        # =========================
        # TIMELINE
        # =========================
        elements.append(Paragraph("Timeline", section))

        for e in events:
            file_path = getattr(e, "file_path", None) or getattr(e, "path", "N/A")

            elements.append(Paragraph(
                f"{e.timestamp} → {e.event_type}",
                normal
            ))
            elements.append(Paragraph(file_path, small))

        elements.append(Spacer(1, 15))

        # =========================
        # 🔥 DYNAMIC CONCLUSION
        # =========================
        elements.append(Paragraph("Conclusion", section))

        if alerts:
            behaviors = []
            mitre_set = set()

            for a in alerts:
                chain = a.get("chain", "")
                mitre_set.add(map_mitre(a))

                if "FILE_DELETED" in chain:
                    behaviors.append("evidence removal")
                if "FILE_MODIFIED" in chain:
                    behaviors.append("data manipulation")
                if "BROWSER_VISIT" in chain:
                    behaviors.append("network/internal access")
                if "LOGIN_FAILED" in chain:
                    behaviors.append("authentication anomalies")

            behaviors = list(set(behaviors))

            conclusion_text = f"""
            The analysis identified {len(alerts)} alerts ({high} HIGH, {med} MEDIUM, {low} LOW).

            Observed patterns indicate: {', '.join(behaviors) if behaviors else 'anomalous activity'}.

            These align with known techniques: {', '.join(mitre_set)}.

            {'Immediate investigation required for high-risk alerts.' if high else 'No immediate critical threat detected, but monitoring is advised.'}
            """
        else:
            conclusion_text = "No suspicious activity detected. System appears normal."

        elements.append(Paragraph(conclusion_text, normal))

        doc.build(elements)
        return response

    except Exception as e:
        print("PDF ERROR:", str(e))
        return HttpResponse(str(e))