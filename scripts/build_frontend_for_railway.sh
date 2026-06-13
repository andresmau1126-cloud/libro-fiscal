# Script de build para Railway
# Este script debe ejecutarse antes del deploy en Railway
cd frontend
npm install
npm run build
cd ..
rm -rf frontend_dist
cp -r frontend/dist frontend_dist
