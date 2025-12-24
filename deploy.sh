#!/bin/bash

# Script de Deploy Simplificado - Scout Pro
# Este script facilita o deploy para Render ou Vercel

set -e  # Exit on error

echo "🚀 Scout Pro - Deploy Automation"
echo "================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if git is clean
if [[ -n $(git status -s) ]]; then
    print_warning "Você tem mudanças não commitadas"
    read -p "Deseja commitar agora? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add -A
        read -p "Mensagem do commit: " commit_msg
        git commit -m "$commit_msg"
        print_success "Commit criado"
    fi
fi

# Push to remote
echo ""
echo "📤 Fazendo push para o GitHub..."
git push origin $(git branch --show-current)
print_success "Código enviado para o GitHub"

echo ""
echo "🎯 Opções de Deploy:"
echo "1) Render (Backend + Frontend + DB)"
echo "2) Vercel (Frontend) + Render (Backend)"
echo "3) Railway (Backend + Frontend + DB)"
echo "4) Docker Local"
echo ""
read -p "Escolha uma opção (1-4): " deploy_option

case $deploy_option in
    1)
        echo ""
        print_success "Deploy via Render selecionado"
        echo ""
        echo "📋 Próximos passos:"
        echo "1. Acesse: https://dashboard.render.com"
        echo "2. Clique em 'New +' > 'Blueprint'"
        echo "3. Conecte seu repositório GitHub"
        echo "4. Selecione: caiofelipead/scouting_scr"
        echo "5. Render detectará o render.yaml automaticamente"
        echo "6. Clique em 'Apply' para iniciar o deploy"
        echo ""
        echo "⏱️  O deploy leva ~5-10 minutos"
        echo ""
        print_warning "Anote as URLs geradas para backend e frontend!"
        ;;

    2)
        echo ""
        print_success "Deploy via Vercel + Render selecionado"
        echo ""
        echo "📋 Frontend (Vercel):"
        echo "1. Acesse: https://vercel.com/new"
        echo "2. Importe: caiofelipead/scouting_scr"
        echo "3. Root Directory: frontend"
        echo "4. Framework Preset: Vite"
        echo "5. Build Command: npm run build"
        echo "6. Output Directory: dist"
        echo "7. Environment Variable:"
        echo "   VITE_API_URL=<URL-DO-BACKEND-RENDER>"
        echo ""
        echo "📋 Backend (Render):"
        echo "1. Acesse: https://dashboard.render.com"
        echo "2. New + > Web Service"
        echo "3. Connect caiofelipead/scouting_scr"
        echo "4. Root Directory: backend"
        echo "5. Runtime: Docker"
        echo "6. Adicione PostgreSQL database"
        echo ""
        ;;

    3)
        echo ""
        print_success "Deploy via Railway selecionado"
        echo ""
        echo "📋 Próximos passos:"
        echo "1. Acesse: https://railway.app"
        echo "2. Login com GitHub"
        echo "3. New Project > Deploy from GitHub repo"
        echo "4. Selecione: caiofelipead/scouting_scr"
        echo "5. Railway detectará o Dockerfile automaticamente"
        echo "6. Adicione PostgreSQL: New > Database > PostgreSQL"
        echo "7. Adicione Redis: New > Database > Redis"
        echo ""
        ;;

    4)
        echo ""
        print_success "Deploy Local (Docker) selecionado"
        echo ""

        # Check if Docker is installed
        if ! command -v docker &> /dev/null; then
            print_error "Docker não está instalado"
            echo "Instale: https://docs.docker.com/get-docker/"
            exit 1
        fi

        # Check if docker-compose is installed
        if ! command -v docker-compose &> /dev/null; then
            print_error "Docker Compose não está instalado"
            echo "Instale: https://docs.docker.com/compose/install/"
            exit 1
        fi

        # Create .env if not exists
        if [ ! -f .env ]; then
            print_warning ".env não encontrado, criando a partir do .env.example..."
            cp .env.example .env
            print_success ".env criado - EDITE AS SENHAS antes de continuar!"
            read -p "Pressione Enter após editar o .env..."
        fi

        echo "🐳 Iniciando containers..."
        docker-compose down -v
        docker-compose up -d --build

        echo ""
        echo "⏳ Aguardando serviços iniciarem (30s)..."
        sleep 30

        echo "🗄️  Executando migrações..."
        docker-compose exec -T backend alembic upgrade head

        echo "👤 Criar usuário admin? (y/n)"
        read -p "" -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose exec backend python create_admin.py
        fi

        echo ""
        print_success "Deploy local concluído!"
        echo ""
        echo "🌐 Acesse a aplicação:"
        echo "   Frontend: http://localhost"
        echo "   Backend:  http://localhost:8000"
        echo "   API Docs: http://localhost:8000/docs"
        echo ""
        echo "📊 Ver logs:"
        echo "   docker-compose logs -f"
        echo ""
        ;;

    *)
        print_error "Opção inválida"
        exit 1
        ;;
esac

echo ""
print_success "Script concluído!"
echo ""
