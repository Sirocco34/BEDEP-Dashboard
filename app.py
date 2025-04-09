import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Veri Yükle
df = pd.read_excel('AI_Rapor.xlsx', sheet_name="Sayfa1")

# Alanlar
alanlar = [
    'Okuma Becerileri',
    'Fen Okuryazarlığı',
    'Matematik Okuryazarlığı',
    'Problem Çözme Becerileri',
    'Finansal Okuryazarlık'
]

# "G" verilerini temizle ve sayısallaştır
for alan in alanlar:
    df = df[df[alan] != "G"]
    df[alan] = pd.to_numeric(df[alan], errors='coerce')

# Seviyeleri eşle
mapping = {0: "Temel Altı", 1: "Temel", 2: "Orta", 3: "Üst", 4: "İleri"}

# Okul Listesi
okul_listesi = df['Okul'].unique().tolist()
okul_listesi.sort()
okul_options = [{'label': okul, 'value': okul} for okul in okul_listesi]
okul_options.insert(0, {'label': 'Tüm Okullar', 'value': 'Tüm Okullar'})

# Dash Uygulaması Başlat
app = dash.Dash(__name__)
server = app.server

# Layout
app.layout = html.Div([
    html.H1('BEDEP 5. Sınıf Dashboard', style={'textAlign': 'center', 'marginBottom': '30px'}),
    html.Div([
        html.Label('Alan Seçimi:', style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='alan-secimi',
            options=[{'label': alan, 'value': alan} for alan in alanlar],
            value='Okuma Becerileri',
            style={'marginBottom': '20px'}
        ),
        html.Label('Okul Seçimi:', style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='okul-secimi',
            options=okul_options,
            value='Tüm Okullar',
            style={'marginBottom': '20px'}
        ),
        html.H3(id='toplam-ogrenci', style={'marginTop': '20px', 'textAlign': 'center'})
    ], style={'width': '100%', 'padding': '20px'}),
    html.Div([
        dcc.Graph(id='genel-grafik', style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id='okul-grafik', style={'width': '48%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'justifyContent': 'center'})
])

# Callback
@app.callback(
    [Output('genel-grafik', 'figure'),
     Output('okul-grafik', 'figure'),
     Output('toplam-ogrenci', 'children')],
    [Input('alan-secimi', 'value'),
     Input('okul-secimi', 'value')]
)
def update_graphs(selected_area, selected_school):
    df_temp = df.copy()
    df_temp['Level'] = df_temp[selected_area].map(mapping)

    # Genel Grafik
    counts_general = df_temp['Level'].value_counts().reindex(["İleri", "Üst", "Orta", "Temel", "Temel Altı"])
    counts_general = counts_general.fillna(0).astype(int)
    genel_fig = px.pie(
        names=counts_general.index,
        values=counts_general.values,
        hole=0.4,
        title=f"Tüm Okullar - {selected_area}",
        color_discrete_map={
            "İleri": '#E6007E',
            "Üst": '#7F3F98',
            "Orta": '#F7951D',
            "Temel": '#1E4B9E',
            "Temel Altı": '#87CEEB'
        }
    )

    # Okul Bazlı Grafik
    if selected_school != 'Tüm Okullar':
        df_school = df_temp[df_temp['Okul'] == selected_school]
        counts_school = df_school['Level'].value_counts().reindex(["İleri", "Üst", "Orta", "Temel", "Temel Altı"])
        counts_school = counts_school.fillna(0).astype(int)
        okul_fig = px.pie(
            names=counts_school.index,
            values=counts_school.values,
            hole=0.4,
            title=f"{selected_school} - {selected_area}",
            color_discrete_map={
                "İleri": '#E6007E',
                "Üst": '#7F3F98',
                "Orta": '#F7951D',
                "Temel": '#1E4B9E',
                "Temel Altı": '#87CEEB'
            }
        )
    else:
        okul_fig = px.pie(
            names=["Okul Seçilmedi"],
            values=[1],
            hole=0.4,
            title="Okul Seçilmedi"
        )

    toplam_ogrenci = df_temp.shape[0]
    toplam_text = f"Toplam Öğrenci Sayısı: {toplam_ogrenci}"

    return genel_fig, okul_fig, toplam_text

# --- Sadece local test için ---
if __name__ == "__main__":
    app.run_server(debug=True)
