"""
Simple scaffold for Careerwill downloader.
- Handles bearer-token or cookies authentication (placeholder)
- Attempts to discover video manifest URLs (m3u8/mpd) on course pages
- Uses yt-dlp to download manifests (works for non-DRM or already-unencrypted streams)

This is a scaffold: Careerwill uses proprietary delivery and likely DRM. Use this as a starting point.
"""

import os
import re
import json
import logging
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

try:
    import yt_dlp
except Exception:
    yt_dlp = None

logger = logging.getLogger(__name__)


class CareerwillDownloader:
    def __init__(self, bearer_token=None, cookies_file=None, widevine_keys=None, output_dir=None):
        self.session = requests.Session()
        self.bearer_token = bearer_token
        self.cookies_file = cookies_file
        self.widevine_keys = widevine_keys or {}
        self.output_dir = output_dir or os.path.join(os.getcwd(), "careerwill_out")
        os.makedirs(self.output_dir, exist_ok=True)

        # Apply auth
        if bearer_token:
            self.session.headers.update({"Authorization": f"Bearer {bearer_token}"})
        elif cookies_file and os.path.exists(cookies_file):
            # Load cookies from Netscape-format file (simple approach)
            try:
                with open(cookies_file, 'r', encoding='utf8') as f:
                    raw = f.read()
                    # Very simple conversion: look for lines with domain\t...\tname\tvalue
                    for line in raw.splitlines():
                        if line.startswith('#') or not line.strip():
                            continue
                        parts = line.split('\t')
                        if len(parts) >= 7:
                            domain = parts[0]
                            name = parts[5]
                            value = parts[6]
                            self.session.cookies.set(name, value, domain=domain)
            except Exception:
                logger.exception('Failed to load cookies file')

    def fetch_course_page(self, course_url):
        """Fetch course main page HTML."""
        resp = self.session.get(course_url)
        resp.raise_for_status()
        return resp.text

    def discover_manifest_urls(self, html, base_url):
        """Try to discover .m3u8 or .mpd manifest URLs in HTML or embedded scripts."""
        manifests = set()
        # Search for m3u8 or mpd in HTML
        for m in re.findall(r"(https?://[^"]+?\.(?:m3u8|mpd)(?:\?[^\"']*)?)", html):
            manifests.add(m)

        # Search for file urls inside JSON blobs
        soup = BeautifulSoup(html, 'lxml')
        for script in soup.find_all('script'):
            if not script.string:
                continue
            for m in re.findall(r"(https?://[^"]+?\.(?:m3u8|mpd)(?:\?[^\"']*)?)", script.string):
                manifests.add(m)

        # Normalize relative URLs if any (rare)
        normalized = set()
        for url in manifests:
            if url.startswith('/'):
                normalized.add(urljoin(base_url, url))
            else:
                normalized.add(url)
        return list(normalized)

    def download_manifest_with_ytdlp(self, manifest_url, out_dir, filename=None):
        if not yt_dlp:
            raise RuntimeError('yt_dlp not installed in environment')

        ydl_opts = {
            'outtmpl': os.path.join(out_dir, filename or '%(title)s.%(ext)s'),
            'allow_unplayable_formats': True,
            'noplaylist': True,
            'quiet': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info('Downloading manifest: %s', manifest_url)
            ydl.download([manifest_url])

    def download_course(self, course_url):
        """Main orchestrator: fetch page, discover manifests, download them."""
        logger.info('Fetching course page: %s', course_url)
        html = self.fetch_course_page(course_url)
        manifests = self.discover_manifest_urls(html, course_url)
        logger.info('Found %d manifest(s)', len(manifests))

        if not manifests:
            logger.warning('No manifest URLs found in page. The site may use an API or DRM-protected packaging.')
            # Attempt basic API exploration: look for JSON endpoints referenced on page
            # This is left as an exercise for further automation
            return

        for i, m in enumerate(manifests, start=1):
            out_subdir = os.path.join(self.output_dir, f'manifest_{i}')
            os.makedirs(out_subdir, exist_ok=True)
            try:
                self.download_manifest_with_ytdlp(m, out_subdir)
            except Exception:
                logger.exception('Failed to download manifest: %s', m)

    def get_enrolled_courses(self, dashboard_url=None):
        """Attempt to discover enrolled course URLs from the user's dashboard/home page.

        This is a heuristic-based scraper: it fetches `dashboard_url` (or the site root)
        and looks for links that contain '/course/' or '/learn/'. It requires an
        authenticated session (bearer token or cookies).
        """
        candidates = set()
        if dashboard_url is None:
            dashboard_url = 'https://web.careerwill.com/'

        try:
            resp = self.session.get(dashboard_url)
            resp.raise_for_status()
        except Exception:
            logger.exception('Failed to fetch dashboard URL: %s', dashboard_url)
            return []

        soup = BeautifulSoup(resp.text, 'lxml')
        for a in soup.find_all('a', href=True):
            href = a['href']
            # normalize
            if href.startswith('/'):
                href = urljoin(dashboard_url, href)
            if '/course/' in href or '/learn/' in href:
                candidates.add(href.split('?')[0])

        results = sorted(candidates)
        logger.info('Discovered %d enrolled course(s)', len(results))
        return results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--course-url', dest='course_url', required=False,
                        help='Single course URL to download')
    parser.add_argument('-b', '--bearer', dest='bearer')
    parser.add_argument('-o', '--out', dest='out')
    parser.add_argument('--list-enrolled', dest='list_enrolled', action='store_true',
                        help='List courses you are enrolled in (uses auth)')
    parser.add_argument('--download-enrolled', dest='download_enrolled', action='store_true',
                        help='Download all discovered enrolled courses')
    args = parser.parse_args()

    dl = CareerwillDownloader(bearer_token=args.bearer, cookies_file='cookies.txt' if not args.bearer else None,
                               output_dir=(args.out or None))

    if args.list_enrolled or args.download_enrolled:
        courses = dl.get_enrolled_courses()
        if args.list_enrolled:
            print('\n'.join(courses))
        if args.download_enrolled:
            for course in courses:
                print(f'\n=== Downloading course: {course} ===')
                dl.download_course(course)
    elif args.course_url:
        dl.download_course(args.course_url)
    else:
        parser.print_help()
