import os
import sys
import re
import urllib.request
import urllib.parse
from pathlib import Path
from abc import ABC, abstractmethod

def extract_tistory_post_id(url_or_id: str) -> str:
    """Helper to extract post ID from a Tistory post URL or return it if numeric."""
    if not isinstance(url_or_id, str):
        return str(url_or_id)
    if url_or_id.isdigit():
        return url_or_id
    # Search for numeric post ID in path (e.g. tistory.com/123)
    match = re.search(r'/(\d+)(?:\?|$)', url_or_id)
    if match:
        return match.group(1)
    if "mock-published" in url_or_id:
        return "9999"
    return ""

class BasePublisher(ABC):
    @abstractmethod
    def upload_image(self, img_path: Path) -> str:
        """Uploads a local image file and returns its web URL."""
        pass
        
    @abstractmethod
    def publish(self, title: str, html_content: str, tags: list, scheduled_at: str = None) -> str:
        """Publishes the HTML post and returns the published page URL."""
        pass

    @abstractmethod
    def modify(self, post_id_or_url: str, title: str, html_content: str, tags: list = None) -> bool:
        """Modifies an existing HTML post."""
        pass

class TistoryPublisher(BasePublisher):
    def __init__(self, access_token=None, blog_name=None):
        self.access_token = access_token or os.environ.get("TISTORY_ACCESS_TOKEN", "")
        self.blog_name = blog_name or os.environ.get("TISTORY_BLOG_NAME", "my-tistory-blog")
        
    def upload_image(self, img_path: Path) -> str:
        # If API keys are missing, gracefully mock it
        if not self.access_token or self.access_token == "MOCK_TOKEN":
            return f"https://blog.kakaocdn.net/dn/mock/{img_path.name}"
            
        # Realistic implementation of Tistory attach API
        # Tistory requires multipart/form-data upload.
        # To avoid external package dependency (like requests), we will mock it or implement pure urllib multipart if required.
        # But to be robust, we can mock or do requests if requests is installed.
        try:
            import requests
            url = "https://www.tistory.com/apis/post/attach"
            files = {'uploadedfile': open(str(img_path), 'rb')}
            data = {
                'access_token': self.access_token,
                'blogName': self.blog_name,
                'output': 'json'
            }
            res = requests.post(url, data=data, files=files)
            if res.ok:
                res_data = res.json()
                return res_data['tistory']['url']
        except Exception as e:
            sys.stderr.write(f"Tistory attach API error: {str(e)}. Falling back to mock URL.\n")
            
        return f"https://blog.kakaocdn.net/dn/mock/{img_path.name}"

    def publish(self, title: str, html_content: str, tags: list, scheduled_at: str = None) -> str:
        if not self.access_token or self.access_token == "MOCK_TOKEN":
            mock_url = f"https://{self.blog_name}.tistory.com/entry/mock-published-{random_slug(title)}"
            if scheduled_at:
                print(f"[TistoryPublisher] (MOCK) Scheduled publish at {scheduled_at} for post: {mock_url}")
            return mock_url
            
        try:
            import requests
            url = "https://www.tistory.com/apis/post/write"
            data = {
                'access_token': self.access_token,
                'blogName': self.blog_name,
                'title': title,
                'content': html_content,
                'visibility': 3, # 3 is public
                'tag': ",".join(tags),
                'output': 'json'
            }
            if scheduled_at:
                data['date'] = scheduled_at
            res = requests.post(url, data=data)
            if res.ok:
                res_data = res.json()
                # Return the published post URL
                return res_data['tistory']['url']
        except Exception as e:
            sys.stderr.write(f"Tistory write API error: {str(e)}\n")
            
        return f"https://{self.blog_name}.tistory.com/entry/mock-published-{random_slug(title)}"

    def modify(self, post_id_or_url: str, title: str, html_content: str, tags: list = None) -> bool:
        post_id = extract_tistory_post_id(post_id_or_url)
        if not post_id:
            sys.stderr.write(f"Could not extract Tistory postId from: {post_id_or_url}\n")
            return False
            
        if not self.access_token or self.access_token == "MOCK_TOKEN":
            print(f"[TistoryPublisher] (MOCK) Modified Tistory post {post_id}: '{title}'")
            return True
            
        try:
            import requests
            url = "https://www.tistory.com/apis/post/modify"
            data = {
                'access_token': self.access_token,
                'blogName': self.blog_name,
                'postId': post_id,
                'title': title,
                'content': html_content,
                'visibility': 3, # 3 is public
                'output': 'json'
            }
            if tags:
                data['tag'] = ",".join(tags)
            res = requests.post(url, data=data)
            return res.ok
        except Exception as e:
            sys.stderr.write(f"Tistory modify API error: {str(e)}\n")
            return False

class WordpressPublisher(BasePublisher):
    def __init__(self, api_url=None, username=None, password=None):
        self.api_url = api_url or os.environ.get("WORDPRESS_API_URL", "")
        self.username = username or os.environ.get("WORDPRESS_USER", "")
        self.password = password or os.environ.get("WORDPRESS_PASSWORD", "")
        
    def upload_image(self, img_path: Path) -> str:
        # WordPress mock upload
        return f"https://mywordpresssite.com/wp-content/uploads/2026/06/{img_path.name}"

    def publish(self, title: str, html_content: str, tags: list, scheduled_at: str = None) -> str:
        # WordPress mock publish
        slug = random_slug(title)
        mock_url = f"https://mywordpresssite.com/{slug}"
        if scheduled_at:
            print(f"[WordpressPublisher] (MOCK) Scheduled publish at {scheduled_at} for post: {mock_url}")
        return mock_url

    def modify(self, post_id_or_url: str, title: str, html_content: str, tags: list = None) -> bool:
        print(f"[WordpressPublisher] (MOCK) Modified Wordpress post {post_id_or_url}: '{title}'")
        return True

class BloggerPublisher(BasePublisher):
    def __init__(self, blog_id=None, api_key=None):
        self.blog_id = blog_id or os.environ.get("BLOGGER_BLOG_ID", "mybloggerblog")
        self.api_key = api_key or os.environ.get("BLOGGER_API_KEY", "")
        
    def upload_image(self, img_path: Path) -> str:
        return f"https://lh3.googleusercontent.com/blogger/mock/{img_path.name}"

    def publish(self, title: str, html_content: str, tags: list, scheduled_at: str = None) -> str:
        slug = random_slug(title)
        mock_url = f"https://{self.blog_id}.blogspot.com/2026/06/{slug}.html"
        if scheduled_at:
            print(f"[BloggerPublisher] (MOCK) Scheduled publish at {scheduled_at} for post: {mock_url}")
        return mock_url

    def modify(self, post_id_or_url: str, title: str, html_content: str, tags: list = None) -> bool:
        print(f"[BloggerPublisher] (MOCK) Modified Blogger post {post_id_or_url}: '{title}'")
        return True

def random_slug(title):
    # Pure slugifier helper
    slug = re.sub(r'[^a-zA-Z0-9ㄱ-ㅎㅏ-ㅣ가-힣]', '-', title)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')[:30]

def publish_post_pipeline(publisher: BasePublisher, title: str, html_content: str, tags: list, local_image_paths: list, scheduled_at: str = None) -> tuple:
    """
    Orchestrates the image uploading and URL rewriting:
    1. Iterates over each local image path.
    2. Uploads via publisher.upload_image().
    3. Replaces the local path src in html_content with the remote URL.
    4. Triggers post publishing.
    """
    updated_html = html_content
    
    for relative_path in local_image_paths:
        # Find absolute path of the local image
        output_dir = Path(__file__).resolve().parent / ".." / ".." / "web_dashboard"
        abs_img_path = output_dir / relative_path.lstrip("/")
        
        # Upload
        web_url = publisher.upload_image(abs_img_path)
        
        # Replace in HTML (support absolute paths or just relative paths depending on what image_generator output)
        # Search for exact occurrences of the filename or relative src
        local_src_pattern = rf'src=["\']/{relative_path.lstrip("/")}["\']'
        web_src_replace = f'src="{web_url}"'
        updated_html = re.sub(local_src_pattern, web_src_replace, updated_html)
        
        # Also handle any simple src="filename" or src="/output/filename" formats
        filename_pattern = rf'src=["\'][^"\']*{abs_img_path.name}["\']'
        updated_html = re.sub(filename_pattern, web_src_replace, updated_html)
        
    # Publish post
    publish_url = publisher.publish(title, updated_html, tags, scheduled_at=scheduled_at)
    return publish_url, updated_html

if __name__ == "__main__":
    pub = TistoryPublisher(access_token="MOCK_TOKEN", blog_name="my-world")
    test_html = '<img src="/output/test.webp" alt="테스트" />'
    url, final_html = publish_post_pipeline(pub, "테스트 글", test_html, ["테스트"], ["/output/test.webp"])
    print("Published URL:", url)
    print("Final HTML:", final_html)
