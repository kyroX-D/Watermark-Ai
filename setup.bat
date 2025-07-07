@echo off
echo Setting up AI Watermark System...
echo Creating directory structure...
mkdir backend\app\api\endpoints 2>nul
mkdir backend\app\core 2>nul
mkdir backend\app\models 2>nul
mkdir backend\app\schemas 2>nul
mkdir backend\app\services 2>nul
mkdir backend\app\utils 2>nul
mkdir backend\static\watermarks 2>nul
mkdir backend\alembic\versions 2>nul
mkdir frontend\src\components\auth 2>nul
mkdir frontend\src\components\common 2>nul
mkdir frontend\src\components\dashboard 2>nul
mkdir frontend\src\components\watermark 2>nul
mkdir frontend\src\components\subscription 2>nul
mkdir frontend\src\pages 2>nul
mkdir frontend\src\services 2>nul
mkdir frontend\src\hooks 2>nul
mkdir frontend\src\utils 2>nul
mkdir frontend\src\styles 2>nul
mkdir frontend\public 2>nul
echo.
echo Directory structure created!
echo.
echo Now you need to:
echo 1. Copy all the code files into their respective directories
echo 2. Run: cd backend
echo 3. Run: python -m venv venv
echo 4. Run: venv\Scripts\activate
echo 5. Run: pip install psycopg2
echo 6. Run: pip install -r requirements.txt
echo 7. Create and configure .env file
echo 8. Run: uvicorn main:app --reload
echo.
echo For frontend:
echo 1. Open new terminal
echo 2. Run: cd frontend
echo 3. Run: npm install
echo 4. Create and configure .env file
echo 5. Run: npm run dev