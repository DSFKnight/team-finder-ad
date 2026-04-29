from django.core.exceptions import ValidationError

from .constants import GITHUB_DOMAIN


class GithubUrlCleanMixin:
    
    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url:
            if GITHUB_DOMAIN not in url.lower():
                raise ValidationError("Ссылка должна вести на Github")
        return url
    