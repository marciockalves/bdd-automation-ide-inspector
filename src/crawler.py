import httpx

class SimpleCrawler:
    """Realiza a captura do HTML via HTTP puro, sem necessidade de GPU."""
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_html(self, url):
        try:
            # Usamos o httpx para suportar requisições assíncronas no futuro se necessário
            with httpx.Client(headers=self.headers, follow_redirects=True, timeout=10.0) as client:
                response = client.get(url)
                response.raise_for_status() # Levanta erro se o site não carregar (404, 500)
                return response.text
        except Exception as e:
            print(f"Erro no Crawler: {e}")
            return None