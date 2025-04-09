
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
    
    genel_oran = dft["Level"].value_counts(normalize=True).reindex(["İleri", "Üst", "Orta", "Temel", "Temel Altı"]).fillna(0) * 100

    fig_genel = px.bar(
        x=genel_oran.index,
        y=genel_oran.values,
        labels={'x': 'Düzey', 'y': 'Yüzde (%)'},
        title="Tüm Okullar Genel Dağılım",
        color=genel_oran.index,
        color_discrete_map=colors
    )

    if okul != "Tüm Okullar":
        dfo = dft[dft["Okul"] == okul]
        okul_oran = dfo["Level"].value_counts(normalize=True).reindex(["İleri", "Üst", "Orta", "Temel", "Temel Altı"]).fillna(0) * 100
        fig_okul = px.bar(
            x=okul_oran.index,
            y=okul_oran.values,
            labels={'x': 'Düzey', 'y': 'Yüzde (%)'},
            title=f"{okul} Genel Dağılım",
            color=okul_oran.index,
            color_discrete_map=colors
        )

        # Şube bazlı
        sube_df = dfo.groupby('Şube')[alan].mean().reset_index()
        fig_sube = px.bar(
            sube_df,
            x='Şube',
            y=alan,
            labels={'Şube': 'Şube', alan: 'Puan (%)'},
            title=f"{okul} Şube Ortalamaları",
            color='Şube'
        )
    else:
        fig_okul = px.bar(
            x=["Lütfen Okul Seçin"],
            y=[0],
            title="Okul Seçilmedi"
        )
        fig_sube = px.bar(
            x=["Lütfen Okul Seçin"],
            y=[0],
            title="Şube Bilgisi Yok"
        )
        
    fig_genel.update_layout(yaxis=dict(range=[0, 100]))
    fig_okul.update_layout(yaxis=dict(range=[0, 100]))
    
    return fig_genel, fig_okul, fig_sube

# Lokal test için
if __name__ == "__main__":
    app.run_server(debug=True)
