import hashlib

import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
from datetime import datetime
from typing import Union, List, Tuple
import logging


class HespressCommentsScraper:
    """A class to scrape comments from Hespress articles."""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        self.months_mapping = {
            'يناير': 'January', 'فبراير': 'February', 'مارس': 'March',
            'أبريل': 'April', 'ماي': 'May', 'يونيو': 'June',
            'يوليوز': 'July', 'غشت': 'August', 'شتنبر': 'September',
            'أكتوبر': 'October', 'نونبر': 'November', 'دجنبر': 'December'
        }
        self.logger = self._setup_logger()

    def _generate_comment_id(self, user_name, comment_text, date_string):
        """Generates a unique ID for each comment."""
        combined_string = f"{user_name}-{comment_text}-{date_string}"
        return hashlib.sha256(combined_string.encode('utf-8')).hexdigest()

    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger('HespressScraper')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _is_valid_url(self, url: str) -> bool:
        """Validate if the URL is a valid Hespress URL."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.netloc == "www.hespress.com"
        except ValueError:
            return False

    def _arabic_to_english_month(self, arabic_month: str) -> str:
        """Convert Arabic month name to English."""
        return self.months_mapping.get(arabic_month, 'Unknown')

    def _parse_date(self, date_string: str) -> Union[datetime, None]:
        """Parse date string into pandas Timestamp."""
        try:
            date_parts = date_string.strip().split()
            day = int(date_parts[1])
            month = self._arabic_to_english_month(date_parts[2])
            year = int(date_parts[3])
            time_parts = date_parts[-1].split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            return datetime(year, datetime.strptime(month, '%B').month, day, hour, minute)
        except (ValueError, IndexError) as e:
            self.logger.warning(f"Error parsing date: {date_string}. Error: {str(e)}. Returning None.")
            return pd.NaT

    def _fetch_single_article(self, url: str, existing_comment_ids: set) -> Tuple[pd.DataFrame, str]:
        """Fetch comments from a single article URL, excluding existing comments."""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            article_title = soup.find('h1', class_='post-title')
            article_title = article_title.get_text() if article_title else 'Unknown Title'

            comments_data = {
                'User Name': [], 'Comment': [],
                'Date': [], 'Likes': [], 'Article URL': [],
                'Article Title': [], 'comment_id': []
            }

            comments_section = soup.find('ul', {"class": "comment-list hide-comments"})
            if not comments_section:
                self.logger.info(f"No comments found for article: {article_title}")
                return pd.DataFrame(comments_data), article_title

            for comment in comments_section.find_all('li', class_='comment'):
                date_div = comment.find('div', class_='comment-date')
                date_string = date_div.get_text() if date_div else ''
                comment_id = self._generate_comment_id(
                    comment.find('span', class_='fn heey').get_text() if comment.find('span',
                                                                                      class_='fn heey') else 'Unknown',
                    comment.find('p').get_text() if comment.find('p') else 'No comment text found',
                    date_string
                )

                if comment_id in existing_comment_ids:
                    continue  # skip if it already exists

                comments_data['User Name'].append(
                    comment.find('span', class_='fn heey').get_text() if comment.find('span',
                                                                                      class_='fn heey') else 'Unknown'
                )
                comments_data['Comment'].append(
                    comment.find('p').get_text() if comment.find('p') else 'No comment text found'
                )
                comments_data['Date'].append(
                    self._parse_date(date_div.get_text()) if date_div else pd.NaT
                )
                likes_span = comment.find('span', class_='comment-recat-number')
                comments_data['Likes'].append(
                    int(likes_span.get_text()) if likes_span else 0
                )
                comments_data['Article URL'].append(url)
                comments_data['Article Title'].append(article_title)
                comments_data['comment_id'].append(comment_id)

            return pd.DataFrame(comments_data), article_title

        except requests.RequestException as e:
            self.logger.error(f"Error fetching URL {url}: {str(e)}")
            return pd.DataFrame(), 'Error'

    def fetch_comments(self, urls: Union[str, List[str]], existing_comment_ids: set = set()) -> pd.DataFrame:
        """
        Fetch comments, excluding comments with IDs present in existing_comment_ids.
        """
        if isinstance(urls, str):
            urls = [urls]

        all_comments = []
        for url in urls:
            if not self._is_valid_url(url):
                self.logger.warning(f"Invalid URL skipped: {url}")
                continue

            self.logger.info(f"Fetching comments from: {url}")
            df, title = self._fetch_single_article(url, existing_comment_ids)
            if not df.empty:
                all_comments.append(df)
                self.logger.info(f"Successfully fetched {len(df)} comments from '{title}'")

        final_df = pd.concat(all_comments, ignore_index=True) if all_comments else pd.DataFrame()

        return final_df
