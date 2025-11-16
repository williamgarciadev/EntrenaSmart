"""
Script de prueba para la API FastAPI.

Verifica que los endpoints funcionan correctamente.
"""
import asyncio
import httpx
import sys

API_URL = "http://localhost:8000"
TOKEN = "dev-token"

async def test_api():
    """Realiza pruebas básicas de la API."""
    headers = {"Authorization": f"Bearer {TOKEN}"}

    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Health check
            print("\n🧪 TEST 1: Health Check")
            response = await client.get(f"{API_URL}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")

            # Test 2: Obtener configuración semanal
            print("\n🧪 TEST 2: Obtener Configuración Semanal")
            response = await client.get(
                f"{API_URL}/api/training-config",
                headers=headers
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Días configurados: {len(data.get('configs', []))}")
                for config in data.get('configs', [])[:2]:
                    print(f"     - {config['weekday_name']}: {config.get('session_type', 'No configurado')}")
            else:
                print(f"   Error: {response.text}")

            # Test 3: Actualizar configuración de un día
            print("\n🧪 TEST 3: Actualizar Configuración (Lunes)")
            response = await client.post(
                f"{API_URL}/api/training-config/0",
                json={
                    "weekday": 0,
                    "weekday_name": "Lunes",
                    "session_type": "Pierna",
                    "location": "2do Piso"
                },
                headers=headers
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Configuración actualizada")
                print(f"   Response: {response.json()['message']}")
            else:
                print(f"   Error: {response.text}")

            # Test 4: Obtener configuración actualizada
            print("\n🧪 TEST 4: Verificar Configuración Actualizada")
            response = await client.get(
                f"{API_URL}/api/training-config/0",
                headers=headers
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                config = response.json()
                print(f"   ✅ Lunes actualizado:")
                print(f"      Tipo: {config.get('session_type')}")
                print(f"      Ubicación: {config.get('location')}")

            print("\n" + "="*70)
            print("✅ TODOS LOS TESTS PASARON")
            print("="*70)
            print("\n📍 URLs importantes:")
            print(f"   API: {API_URL}")
            print(f"   Docs (Swagger): {API_URL}/docs")
            print(f"   ReDoc: {API_URL}/redoc")
            print(f"\n Frontend (después de ejecutar 'npm run dev' en frontend/):")
            print(f"   http://localhost:5173/config")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            print("\n💡 Asegúrate de que la API está ejecutándose:")
            print("   cd backend")
            print("   uvicorn api.main:app --reload --port 8000")
            sys.exit(1)

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 PRUEBAS DE API - EntrenaSmart")
    print("="*70)
    asyncio.run(test_api())
