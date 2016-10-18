from django.db import models


class Language(models.Model):
    lang_id = models.CharField(max_length=5)
    lang_dc = models.CharField(max_length=30)

    def __str__(self):
        return self.lang_dc


class NavigationBar(models.Model):
    nav_li_id = models.CharField(max_length=10)
    nav_li_dc = models.CharField(max_length=50)
    language = models.ForeignKey(Language)

    def __str__(self):
        return self.nav_li_dc
