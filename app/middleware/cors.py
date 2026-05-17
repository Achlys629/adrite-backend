from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173",
                   "https://devotedly-subtotal-evident.ngrok-free.dev"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
)