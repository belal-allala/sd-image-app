from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Stocker activement l'état des connexions pour éviter le spam
        # mapping {websocket_instance: est_en_cours_de_generation (bool)}
        self.active_connections = {}

    def is_generating(self, websocket: WebSocket) -> bool:
        """Vérifie si une tâche lourde est déjà en cours pour cette connexion."""
        return self.active_connections.get(websocket, False)

    def set_generating(self, websocket: WebSocket, state: bool):
        """Verrouille ou déverrouille les capacités de génération de la connexion."""
        self.active_connections[websocket] = state

    async def send_progress(self, websocket: WebSocket, percentage: float, message: str = ""):
        """
        Envoie une mise à jour standardisée au format JSON sur l'avancement.
        Respecte la structure constante demandée.
        """
        payload = {
            "type": "progress",
            "value": int(percentage),
            "message": message
        }
        await websocket.send_json(payload)

    async def send_image(self, websocket: WebSocket, base64_data: str, format_name: str):
        """
        Envoie l'image finale encodée en base64 au client.
        """
        payload = {
            "type": "image",
            "format": format_name,
            "data": base64_data
        }
        await websocket.send_json(payload)

    async def send_error(self, websocket: WebSocket, error_message: str):
        """
        Envoie un message de type 'error' en cas problème.
        """
        payload = {
            "type": "error",
            "message": error_message
        }
        await websocket.send_json(payload)

    def disconnect(self, websocket: WebSocket):
        """Nettoie la connexion à la fermeture du socket."""
        if websocket in self.active_connections:
            del self.active_connections[websocket]
