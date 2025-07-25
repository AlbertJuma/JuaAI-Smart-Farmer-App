#!/bin/bash

# JuaAI Smart Farmer - Plant Classifier Startup Script
# This script starts both the Flask backend and frontend servers

echo "🌱 Starting JuaAI Smart Farmer Plant Classifier System..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Check ports
echo "🔍 Checking available ports..."
if ! check_port 5000; then
    echo "   Backend port 5000 is busy"
fi

if ! check_port 8000; then
    echo "   Frontend port 8000 is busy"
fi

# Create log directory
mkdir -p logs

# Start Flask backend in background
echo "🚀 Starting Flask backend server on port 5000..."
cd backend
python3 app.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Check if backend is running
if curl -s http://localhost:5000/ > /dev/null; then
    echo "✅ Backend started successfully"
else
    echo "❌ Backend failed to start. Check logs/backend.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend server
echo "🌐 Starting frontend server on port 8000..."
python3 -m http.server 8000 > logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 2

# Check if frontend is running
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Frontend started successfully"
else
    echo "❌ Frontend failed to start. Check logs/frontend.log"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

# Display startup information
echo ""
echo "🎉 JuaAI Smart Farmer Plant Classifier is running!"
echo ""
echo "📱 Frontend: http://localhost:8000"
echo "🔧 Backend API: http://localhost:5000"
echo ""
echo "📋 Quick Start:"
echo "   1. Open http://localhost:8000 in your browser"
echo "   2. Click 'Crop AI' tab"
echo "   3. Upload a plant leaf image"
echo "   4. Click 'Analyze Crop' to get results"
echo ""
echo "📊 Health Check:"
echo "   Backend: curl http://localhost:5000/"
echo "   Frontend: curl http://localhost:8000/"
echo ""
echo "📝 Logs:"
echo "   Backend: tail -f logs/backend.log"
echo "   Frontend: tail -f logs/frontend.log"
echo ""
echo "🛑 To stop the servers:"
echo "   Press Ctrl+C or run: kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Create a function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Keep script running and show status
echo "💡 System is ready! Press Ctrl+C to stop all servers."
echo ""

# Monitor processes
while true; do
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend process died. Check logs/backend.log"
        break
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend process died. Check logs/frontend.log"
        break
    fi
    
    sleep 10
done

cleanup