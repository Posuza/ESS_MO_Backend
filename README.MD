<!-- backend server run command -->
uvicorn app.main:app --reload


<!-- ```bash
cloudflared tunnel --config ~/Desktop/Inno_Project/GUTSESS_BACKEND/guts-config.yml run gtus

``` -->

- The backend will be available at `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`

### Frontend

```bash
cd frontEnd
npm install
npm run dev
```

/Users/user/Desktop/Inno_Project/GUTSESS_BACKEND/guts-config.yml