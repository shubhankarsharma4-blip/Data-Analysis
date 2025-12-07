# 🖥️ How to Run Streamlit Dashboard Locally

## Quick Start

To see the terminal output and run the dashboard locally:

### Option 1: Direct Command (Simplest)

Open PowerShell in your project folder and run:

```powershell
streamlit run streamlit_app.py
```

This will:
- Start the Streamlit server
- Show output in your terminal
- Automatically open your browser
- Display the dashboard at http://localhost:8501

### Option 2: Using the Helper Script

```powershell
.\run.ps1
```

This script:
- Creates/activates virtual environment
- Installs dependencies
- Runs the dashboard

### Option 3: With Specific Port

```powershell
streamlit run streamlit_app.py --server.port 8501
```

---

## What You'll See in Terminal

When Streamlit runs, you'll see output like:

```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

You'll also see:
- Any print statements or logs
- Error messages if something goes wrong
- Debug information

---

## Troubleshooting

### Issue: "Command not found: streamlit"

**Solution**: Install Streamlit first
```powershell
pip install streamlit pandas plotly sqlalchemy
```

### Issue: "Port 8501 already in use"

**Solution**: Use a different port
```powershell
streamlit run streamlit_app.py --server.port 8502
```

### Issue: No output showing

**Solution**: 
1. Make sure you're running in a terminal (not background)
2. Check if the process is already running:
   ```powershell
   netstat -ano | findstr :8501
   ```
3. Stop any existing Streamlit processes

### Issue: "Module not found"

**Solution**: Install missing packages
```powershell
pip install -r requirements.txt
```

---

## Viewing Real-time Output

To see all output in real-time:

1. **Open a new PowerShell/Command Prompt window**
2. **Navigate to your project folder**:
   ```powershell
   cd C:\Python\ecommerce_etl_project
   ```
3. **Run Streamlit** (don't use background):
   ```powershell
   streamlit run streamlit_app.py
   ```

The terminal will show:
- ✅ Loading messages
- ✅ Database initialization status
- ✅ Any errors
- ✅ Access URLs
- ✅ All print/log statements

---

## Stopping the Server

To stop Streamlit:
- Press `Ctrl + C` in the terminal
- Or close the terminal window

---

## Testing Locally Before Deployment

1. **Run locally first**:
   ```powershell
   streamlit run streamlit_app.py
   ```

2. **Check the dashboard**:
   - Open http://localhost:8501
   - Verify all pages work
   - Check for errors

3. **Fix any issues** locally

4. **Then push to GitHub** for Streamlit Cloud deployment

---

## Quick Commands

```powershell
# Run dashboard
streamlit run streamlit_app.py

# Run on different port
streamlit run streamlit_app.py --server.port 8502

# Run with reload disabled (faster)
streamlit run streamlit_app.py --server.runOnSave false

# Check what's running on port 8501
netstat -ano | findstr :8501
```

---

## Need Help?

If you're not seeing output:
1. Make sure you're in the correct directory
2. Check that Streamlit is installed: `streamlit --version`
3. Try running in a new terminal window
4. Check for error messages

---

**Happy coding!** 🚀

