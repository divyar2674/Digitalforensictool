from django.db import models


class FileEvent(models.Model):
    timestamp = models.DateTimeField()

    event_type = models.CharField(max_length=100)
    # FILE_CREATED, FILE_MODIFIED, FILE_DELETED, FILE_ACCESSED

    source = models.CharField(max_length=50)
    # File System / Recycle Bin

    file_name = models.CharField(max_length=255)
    path = models.TextField()

    size = models.BigIntegerField(null=True, blank=True)
    extension = models.CharField(max_length=20, null=True, blank=True)

    created_time = models.DateTimeField(null=True, blank=True)
    modified_time = models.DateTimeField(null=True, blank=True)
    accessed_time = models.DateTimeField(null=True, blank=True)
    deleted_time = models.DateTimeField(null=True, blank=True)

    # extra notes (like system-triggered access)
    note = models.TextField(null=True, blank=True)

    scan_id = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    case = models.ForeignKey('Case', null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self):
        return f"{self.timestamp} - {self.event_type} - {self.file_name}"
class BrowserEvent(models.Model):
    timestamp = models.DateTimeField()

    browser = models.CharField(max_length=50)
    # CHROME / EDGE etc.

    url = models.TextField()
    title = models.TextField(null=True, blank=True)

    visit_count = models.IntegerField(default=0)
    typed_count = models.IntegerField(default=0)

    scan_id = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    case = models.ForeignKey('Case', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.timestamp} - {self.browser} - {self.url}"

class WindowsEvent(models.Model):
    timestamp = models.DateTimeField()

    event_type = models.CharField(max_length=100)
    # LOGIN_SUCCESS, LOGIN_FAILED, PROCESS_CREATED

    username = models.CharField(max_length=255, null=True, blank=True)
    ip_address = models.CharField(max_length=100, null=True, blank=True)

    process_name = models.TextField(null=True, blank=True)

    event_id = models.IntegerField()

    source = models.CharField(max_length=50)
    # Windows / Windows Security

    scan_id = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    case = models.ForeignKey('Case', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.timestamp} - {self.event_type}"
    

# =========================
# 👤 INVESTIGATOR
# =========================
class Investigator(models.Model):
    name = models.CharField(max_length=100)
    badge_id = models.CharField(max_length=50)
    role = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================
# 📁 CASE
# =========================
class Case(models.Model):
    case_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()

    investigator = models.ForeignKey(Investigator, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.case_id


# =========================
# 💻 EVIDENCE (DEVICE)
# =========================
class Evidence(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)

    device_name = models.CharField(max_length=100)
    path = models.CharField(max_length=300)

    # 🔥 optional but important
    hash_value = models.CharField(max_length=256, null=True, blank=True)

    collected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_name} ({self.case.case_id})"


# =========================
# 🔗 CHAIN OF CUSTODY
# =========================
class ChainOfCustody(models.Model):
    evidence = models.ForeignKey(Evidence, on_delete=models.CASCADE)
    investigator = models.ForeignKey(Investigator, on_delete=models.CASCADE)

    action = models.CharField(max_length=100)
    # Collected / Analyzed / Transferred / Report Generated

    timestamp = models.DateTimeField(auto_now_add=True)

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.action} by {self.investigator.name}"
    
