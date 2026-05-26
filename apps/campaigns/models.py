from django.db import models
from apps.contacts.models import Contact


class Campaign(models.Model):
    STATUS = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    name = models.CharField(max_length=200)
    message_template = models.TextField()
    image = models.ImageField(upload_to='campaign_images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS, default='draft')
    delay_min = models.IntegerField(default=5)
    delay_max = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

    @property
    def total_recipients(self):
        return self.recipients.count()

    @property
    def sent_count(self):
        return self.recipients.filter(status='sent').count()

    @property
    def failed_count(self):
        return self.recipients.filter(status='failed').count()

    @property
    def pending_count(self):
        return self.recipients.filter(status='pending').count()

    @property
    def progress(self):
        total = self.total_recipients
        if total == 0:
            return 0
        return int((self.sent_count + self.failed_count) / total * 100)


class CampaignRecipient(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='recipients')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f'{self.contact.name} - {self.status}'

    class Meta:
        ordering = ['pk']
