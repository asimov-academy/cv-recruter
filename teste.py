import asyncio
from ollama.repositories import HTTPXAsyncClient, HTTPXSyncClient
from ollama.services import AsyncCompletionService, SyncCompletionService
from ollama.models import GenerateCompletionRequest

# Configurações padrão
DEFAULT_MODEL = "llama3"
DEFAULT_KEEP_ALIVE = "10s"  # Exemplo de configuração customizada

# Versão Assíncrona
async def main_async():
    async_client = HTTPXAsyncClient(base_url="http://localhost:11434/api")
    service = AsyncCompletionService(async_client, model=DEFAULT_MODEL, keep_alive=DEFAULT_KEEP_ALIVE)
    
    request = GenerateCompletionRequest(prompt="Why is the sky blue?")
    response = await service.generate_completion(request)
    print(response)

# Versão Síncrona
def main_sync():
    sync_client = HTTPXSyncClient(base_url="http://localhost:11434/api")
    service = SyncCompletionService(sync_client, model=DEFAULT_MODEL, keep_alive=DEFAULT_KEEP_ALIVE)
    
    request = GenerateCompletionRequest(prompt="Why is the sky blue?")
    response = service.generate_completion(request)
    print(response.model_dump())

if __name__ == "__main__":
    # Execute assíncrono
    # asyncio.run(main_async())
    
    # Execute síncrono
    main_sync()
