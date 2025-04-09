
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Veri yükleme
df = pd.read_excel("AI_Rapor.xlsx", sheet_name="Sayfa1")

# Girmeyenleri çıkar, sayısallaştır
alanlar = [
    'Okuma Becerileri',
    'Fen Okuryazarlığı',
    'Matematik Okuryazarlığı',
    'Problem Çözme Becerileri',
    'Finansal Okuryazarlık'
]
for alan in alanlar:
    df = df[df[alan] != "G"]
    df[alan] = pd.to_numeric(df[alan], errors="coerce")

# Düzey eşlemesi
mapping = {0: "Temel Altı", 1: "Temel", 2: "Orta", 3: "Üst", 4: "İleri"}
colors = {
    "İleri": "#E6007E",
    "Üst": "#7F3F98",
    "Orta": "#F7951D",
    "Temel": "#1E4B9E",
    "Temel Altı": "#87CEEB"
}

# Dash app
app = dash.Dash(__name__)
server = app.server

# Layout
app.layout = html.Div([
    html.H1("BEDEP 5. Sınıf Dashboard", style={'textAlign': 'center'}),
    
    html.Div([
        html.Label("Alan Seçimi"),
        dcc.Dropdown(
            id="alan-dropdown",
            options=[{"label": alan, "value": alan} for alan in alanlar],
            value="Okuma Becerileri",
            style={'marginBottom': '20px'}
        ),
        html.Label("Okul Seçimi"),
        dcc.Dropdown(
            id="okul-dropdown",
            options=[{"label": "Tüm Okullar", "value": "Tüm Okullar"}] +
                    [{"label": okul, "value": okul} for okul in sorted(df["Okul"].unique())],
            value="Tüm Okullar"
        )
    ], style={'width': '50%', 'margin': 'auto'}),
    
    html.Div([
        dcc.Graph(id="genel-ortalama", style={'display': 'inline-block', 'width': '32%'}),
        dcc.Graph(id="okul-ortalama", style={'display': 'inline-block', 'width': '32%'}),
        dcc.Graph(id="sube-ortalama", style={'display': 'inline-block', 'width': '32%'})
    ], style={'display': 'flex', 'justifyContent': 'center', 'marginTop': '30px'})
])

# Callback
@app.callback(
    [Output("genel-ortalama", "figure"),
     Output("okul-ortalama", "figure"),
     Output("sube-ortalama", "figure")],
    [Input("alan-dropdown", "value"),
     Input("okul-dropdown", "value")]
)
def update_graphs(alan, okul):
    dft = df.copy()
    dft["Level"] = dft[alan].map(mapping)
    
    genel_counts = dft["Level"].value_counts(normalize=True).reindex(["İleri", "Üst", "Orta", "Temel", "Temel Altı"]).fillna(0)
    genel_cum = genel_counts.cumsum() * 100  # kılavuz için

    # Genel grafiği
    genel_fig = px.bar(
        dft,
        x=["Genel"] * len(dft),
        color="Level",
        barmode="stack",
        color_discrete_map=colors,
        category_orders={"Level": ["Temel Altı", "Temel", "Orta", "Üst", "İleri"]}
    )
    genel_fig.update_layout(
        yaxis=dict(title="Yüzde (%)", range=[0, 100]),
        title="Genel Yeterlik Dağılımı"
    )

    shapes = []
    for val in genel_cum[:-1]:  # Sonuncu %100 olduğu için çizmiyoruz
        shapes.append(dict(
            type="line",
            x0=-0.5, x1=0.5,
            y0=val, y1=val,
            line=dict(color="red", width=1, dash="dash")
        ))
    genel_fig.update_layout(shapes=shapes)

    # Okul grafiği
    if okul != "Tüm Okullar":
        okul_df = dft[dft["Okul"] == okul]
        okul_fig = px.bar(
            okul_df,
            x=["Seçilen Okul"] * len(okul_df),
            color="Level",
            barmode="stack",
            color_discrete_map=colors,
            category_orders={"Level": ["Temel Altı", "Temel", "Orta", "Üst", "İleri"]}
        )
        okul_fig.update_layout(
            yaxis=dict(title="Yüzde (%)", range=[0, 100]),
            title=f"{okul} Yeterlik Dağılımı",
            shapes=shapes  # aynı kılavuz çizgiler burada da
        )

        # Şubeler grafiği
        sube_fig = px.bar(
            okul_df,
            x="Şube",
            color="Level",
            barmode="stack",
            color_discrete_map=colors,
            category_orders={"Level": ["Temel Altı", "Temel", "Orta", "Üst", "İleri"]}
        )
        sube_fig.update_layout(
            yaxis=dict(title="Yüzde (%)", range=[0, 100]),
            title=f"{okul} Şubeler Yeterlik Dağılımı",
            shapes=shapes  # burada da
        )
    else:
        okul_fig = px.bar(x=["Lütfen Okul Seçin"], y=[0], title="Okul Seçilmedi")
        sube_fig = px.bar(x=["Lütfen Okul Seçin"], y=[0], title="Şube Bilgisi Yok")
        
    return genel_fig, okul_fig, sube_fig

# Lokal test için
if __name__ == "__main__":
    app.run_server(debug=True)
