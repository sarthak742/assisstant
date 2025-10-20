import os
import logging
import webview

from modules.memory_manager import MemoryManager
from modules.ai_chat_module import AIChatModule

logger = logging.getLogger('Jarvis.Desktop')
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class API:
    def __init__(self):
        self.memory = MemoryManager()
        self.chat = AIChatModule(self.memory)

    def send_message(self, message: str):
        try:
            self.memory.store_interaction('user', message)
            response = self.chat.generate_response(message)
            self.memory.store_interaction('jarvis', response)
            return {'response': response}
        except Exception as e:
            logger.exception('send_message failed')
            return {'error': str(e)}

    def get_recent_interactions(self, count: int = 10):
        try:
            return self.memory.get_recent_interactions(count)
        except Exception as e:
            logger.exception('get_recent_interactions failed')
            return []

    def clear_memory(self):
        try:
            self.memory.clear_interactions()
            self.memory.clear_context()
            return {'ok': True}
        except Exception as e:
            logger.exception('clear_memory failed')
            return {'ok': False, 'error': str(e)}


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    preview_path = os.path.join(base_dir, 'frontend', 'public', 'preview.html')
    if not os.path.exists(preview_path):
        raise RuntimeError(f'preview.html not found at {preview_path}')
    url = 'file:///' + preview_path.replace('\\', '/')

    api = API()
    webview.create_window('Jarvis', url, js_api=api, width=1100, height=720)
    webview.start()


if __name__ == '__main__':
    main()