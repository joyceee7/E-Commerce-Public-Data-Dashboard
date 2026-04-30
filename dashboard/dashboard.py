import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st

# ==========================================
# Konfigurasi Halaman
# ==========================================
st.set_page_config(page_title="E-Commerce Analytics Dashboard", page_icon="🛍️", layout="wide")
sns.set(style='darkgrid')

# ==========================================
# Kamus Kode State Brazil
# ==========================================
STATE_NAMES = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AM': 'Amazonas', 'AP': 'Amapá',
    'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
    'GO': 'Goiás', 'MA': 'Maranhão', 'MG': 'Minas Gerais', 'MS': 'Mato Grosso do Sul',
    'MT': 'Mato Grosso', 'PA': 'Pará', 'PB': 'Paraíba', 'PE': 'Pernambuco',
    'PI': 'Piauí', 'PR': 'Paraná', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
    'RO': 'Rondônia', 'RR': 'Roraima', 'RS': 'Rio Grande do Sul', 'SC': 'Santa Catarina',
    'SE': 'Sergipe', 'SP': 'São Paulo', 'TO': 'Tocantins'
}

# ==========================================
# Load Dataset
# ==========================================
@st.cache_data
def load_data():
    orders = pd.read_csv('orders_dataset.csv')
    order_items = pd.read_csv('order_items_dataset.csv')
    products = pd.read_csv('products_dataset.csv')
    categories = pd.read_csv('product_category_name_translation.csv')
    customers = pd.read_csv('customers_dataset.csv')
    payments = pd.read_csv('order_payments_dataset.csv')

    for col in ['order_purchase_timestamp', 'order_approved_at',
                'order_delivered_carrier_date', 'order_delivered_customer_date',
                'order_estimated_delivery_date']:
        orders[col] = pd.to_datetime(orders[col], errors='coerce')

    # Hapus payment_value = 0 (sesuai notebook)
    payments = payments[payments['payment_value'] > 0]

    return orders, order_items, products, categories, customers, payments

orders, order_items, products, categories, customers, payments = load_data()

# ==========================================
# Header
# ==========================================
st.title("🛍️ E-Commerce Public Data Dashboard")
st.markdown("**Oleh:** Joyce Abigail Gracia Zebua")
st.markdown("---")

# ==========================================
# SIDEBAR: Filter Global — Tanggal Dipisah
# ==========================================
st.sidebar.header("⚙️ Filter Data")

min_date = orders['order_purchase_timestamp'].min().date()
max_date = orders['order_purchase_timestamp'].max().date()

start_date = st.sidebar.date_input(
    label="📅 Tanggal Mulai",
    value=min_date,
    min_value=min_date,
    max_value=max_date,
    key="start_date"
)

end_date = st.sidebar.date_input(
    label="📅 Tanggal Akhir",
    value=max_date,
    min_value=min_date,
    max_value=max_date,
    key="end_date"
)

if start_date > end_date:
    st.sidebar.error("⚠️ Tanggal mulai tidak boleh melebihi tanggal akhir.")
    start_date, end_date = min_date, max_date

# Filter status pesanan
all_statuses = sorted(orders['order_status'].dropna().unique().tolist())
selected_statuses = st.sidebar.multiselect(
    "📦 Status Pesanan:",
    options=all_statuses,
    default=['delivered']
)
if not selected_statuses:
    selected_statuses = all_statuses

# Terapkan filter
filtered_orders = orders[
    (orders['order_purchase_timestamp'].dt.date >= start_date) &
    (orders['order_purchase_timestamp'].dt.date <= end_date) &
    (orders['order_status'].isin(selected_statuses))
].copy()

st.sidebar.markdown("---")
st.sidebar.metric("Total Pesanan (aktif)", f"{len(filtered_orders):,}")
st.sidebar.caption(f"📆 {start_date} s/d {end_date}")

# ==========================================
# KPI
# ==========================================
st.subheader("📊 Ringkasan KPI")

merged_kpi = filtered_orders.merge(order_items[['order_id', 'price']], on='order_id', how='left')
total_revenue = merged_kpi['price'].sum()
total_orders = filtered_orders['order_id'].nunique()
total_customers = filtered_orders['customer_id'].nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("🧾 Total Pesanan", f"{total_orders:,}")
k2.metric("💰 Total Pendapatan", f"BRL {total_revenue:,.0f}")
k3.metric("👤 Pelanggan Unik", f"{total_customers:,}")
k4.metric("🛒 Rata-rata Nilai Pesanan", f"BRL {avg_order_value:,.2f}")

st.markdown("---")

# ==========================================
# 1. Tren Jumlah Pesanan
# ==========================================
st.subheader("📈 Tren Jumlah Pesanan")

freq = st.radio("Pilih Frekuensi Waktu:", ('Bulanan', 'Harian'), horizontal=True)

if not filtered_orders.empty:
    if freq == 'Bulanan':
        filtered_orders['period'] = filtered_orders['order_purchase_timestamp'].dt.to_period('M').astype(str)
    else:
        filtered_orders['period'] = filtered_orders['order_purchase_timestamp'].dt.to_period('D').astype(str)

    trend_data = filtered_orders.groupby('period').size().reset_index(name='order_count')

    fig1, ax1 = plt.subplots(figsize=(13, 5))
    sns.lineplot(data=trend_data, x='period', y='order_count', marker='o', color='#1f77b4', ax=ax1)

    n_ticks = len(trend_data)
    step = max(1, n_ticks // 15)
    tick_pos = list(range(0, n_ticks, step))
    ax1.set_xticks(tick_pos)
    ax1.set_xticklabels(trend_data['period'].iloc[tick_pos], rotation=45, ha='right')
    ax1.set_xlabel("Periode Waktu")
    ax1.set_ylabel("Jumlah Pesanan")
    ax1.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.tight_layout()
    st.pyplot(fig1)

    peak_period = trend_data.loc[trend_data['order_count'].idxmax(), 'period']
    peak_val = trend_data['order_count'].max()
    avg_val = trend_data['order_count'].mean()
    st.info(
        f"💡 **Insight:** Puncak pesanan terjadi pada periode **{peak_period}** "
        f"dengan **{peak_val:,} pesanan**. Rata-rata pesanan per periode: **{avg_val:,.0f}**. "
        f"Gunakan tampilan harian untuk melihat pola mingguan secara lebih detail."
    )
else:
    st.warning("Tidak ada data pada rentang tanggal yang dipilih.")

st.markdown("---")

# ==========================================
# 2. Kategori Produk Pendapatan Tertinggi
# ==========================================
st.subheader("💰 Kategori Produk dengan Pendapatan Tertinggi")

top_n_cat = st.slider("Tampilkan Top N Kategori:", min_value=5, max_value=20, value=10, step=1)

if not filtered_orders.empty:
    merged_cat = (
        filtered_orders[['order_id']]
        .merge(order_items[['order_id', 'product_id', 'price']], on='order_id')
        .merge(products[['product_id', 'product_category_name']], on='product_id')
        .merge(categories, on='product_category_name', how='left')
    )
    merged_cat['product_category_name_english'] = (
        merged_cat['product_category_name_english']
        .fillna(merged_cat['product_category_name'])
    )

    revenue_category = (
        merged_cat.groupby('product_category_name_english')['price']
        .sum()
        .sort_values(ascending=False)
        .head(top_n_cat)
    )

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    bars = sns.barplot(x=revenue_category.values, y=revenue_category.index, palette='viridis', ax=ax2)
    max_val = revenue_category.values.max()
    for bar, val in zip(bars.patches, revenue_category.values):
        ax2.text(bar.get_width() + max_val * 0.01,
                 bar.get_y() + bar.get_height() / 2,
                 f'BRL {val:,.0f}', va='center', fontsize=8)
    ax2.set_xlabel("Total Pendapatan (BRL)")
    ax2.set_ylabel("Kategori Produk")
    ax2.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K')
    )
    plt.tight_layout()
    st.pyplot(fig2)

    top1 = revenue_category.index[0]
    top1_val = revenue_category.values[0]
    top2 = revenue_category.index[1] if len(revenue_category) > 1 else "-"
    st.info(
        f"💡 **Insight:** Kategori **{top1}** mendominasi pendapatan dengan total **BRL {top1_val:,.0f}**, "
        f"diikuti oleh **{top2}**. Pastikan stok kategori unggulan ini selalu tersedia "
        f"untuk memaksimalkan pendapatan."
    )
else:
    st.warning("Tidak ada data pada rentang tanggal yang dipilih.")

st.markdown("---")

# ==========================================
# 3. Analisis RFM (sesuai notebook)
# ==========================================
st.subheader("👥 Segmentasi Pelanggan (RFM Analysis)")

if not filtered_orders.empty:
    # Gabungkan orders + customers + payments (sesuai notebook)
    rfm_base = filtered_orders.merge(customers[['customer_id', 'customer_unique_id']], on='customer_id', how='inner')

    # Agregasi payment_value per order_id untuk hindari duplikasi cicilan
    order_payments = payments.groupby('order_id')['payment_value'].sum().reset_index()
    rfm_base = rfm_base.merge(order_payments, on='order_id', how='inner')

    # Tanggal referensi
    recent_date = rfm_base['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

    # Hitung R, F, M per customer_unique_id
    rfm = rfm_base.groupby('customer_unique_id').agg(
        recency=('order_purchase_timestamp', lambda x: (recent_date - x.max()).days),
        frequency=('order_id', 'nunique'),
        monetary=('payment_value', 'sum')
    ).reset_index()

    # Scoring RFM 1-5 (sesuai notebook)
    rfm['R_Score'] = pd.qcut(rfm['recency'], q=5, labels=[5, 4, 3, 2, 1])
    rfm['M_Score'] = pd.qcut(rfm['monetary'], q=5, labels=[1, 2, 3, 4, 5])
    # Frequency pakai rank() karena mayoritas belanja 1x (duplicate bins)
    rfm['F_Score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
    rfm['RFM_Total'] = rfm[['R_Score', 'F_Score', 'M_Score']].astype(int).sum(axis=1)

    # Threshold Top 5%
    top_5_threshold = rfm['RFM_Total'].quantile(0.95)
    top_5_customers = rfm[rfm['RFM_Total'] >= top_5_threshold].sort_values(
        by=['RFM_Total', 'monetary'], ascending=[False, False]
    )

    # KPI RFM
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("⏱️ Rata-rata Recency (Hari)", f"{rfm['recency'].mean():.1f}")
    col2.metric("🔁 Rata-rata Frequency", f"{rfm['frequency'].mean():.2f}")
    col3.metric("💵 Rata-rata Monetary", f"BRL {rfm['monetary'].mean():.2f}")
    col4.metric("🏆 Pelanggan Top 5%", f"{len(top_5_customers):,}")

    st.markdown(f"**Ambang batas skor RFM Top 5%: ≥ {top_5_threshold:.0f}**")

    # Tab visualisasi
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Distribusi Skor RFM",
        "🏆 Top Pelanggan",
        "⏱️ Recency",
        "💵 Monetary"
    ])

    with tab1:
        # Distribusi total skor RFM (sesuai notebook)
        fig_rfm, ax_rfm = plt.subplots(figsize=(10, 5))
        sns.countplot(data=rfm, x='RFM_Total', palette='viridis', ax=ax_rfm)
        ax_rfm.set_title('Distribusi Total Skor RFM Pelanggan', fontsize=14)
        ax_rfm.set_xlabel('Total Skor RFM (Semakin tinggi = semakin loyal)', fontsize=12)
        ax_rfm.set_ylabel('Jumlah Pelanggan', fontsize=12)
        ax_rfm.axvline(
            x=rfm['RFM_Total'].unique().tolist().index(int(top_5_threshold))
                if int(top_5_threshold) in rfm['RFM_Total'].unique() else -1,
            color='red', linestyle='--', linewidth=2,
            label=f'Batas Top 5% (Skor ≥ {top_5_threshold:.0f})'
        )
        ax_rfm.legend()
        plt.tight_layout()
        st.pyplot(fig_rfm)

    with tab2:
        # Tabel top 10 pelanggan paling loyal
        top_n_rfm = st.selectbox("Tampilkan Top N Pelanggan:", [5, 10, 15, 20], index=1)
        display_cols = top_5_customers[['customer_unique_id', 'recency', 'frequency', 'monetary',
                                        'R_Score', 'F_Score', 'M_Score', 'RFM_Total']].head(top_n_rfm).copy()
        display_cols.columns = ['Customer ID', 'Recency (Hari)', 'Frequency', 'Monetary (BRL)',
                                 'R Score', 'F Score', 'M Score', 'RFM Total']
        display_cols['Monetary (BRL)'] = display_cols['Monetary (BRL)'].map(lambda x: f"BRL {x:,.2f}")
        st.dataframe(display_cols, use_container_width=True)

    with tab3:
        top_n_r = st.slider("Top N pelanggan teraktif (Recency):", 5, 20, 10, key='rfm_r')
        fig_r, ax_r = plt.subplots(figsize=(10, 4))
        top_r = rfm.sort_values('recency').head(top_n_r).copy()
        top_r['short_id'] = top_r['customer_unique_id'].str[:10] + '...'
        sns.barplot(data=top_r, x='short_id', y='recency', palette='Blues_r', ax=ax_r)
        ax_r.set_xlabel("Customer ID (disingkat)")
        ax_r.set_ylabel("Hari Sejak Transaksi Terakhir")
        ax_r.set_title(f"Top {top_n_r} Pelanggan dengan Recency Terkecil (Paling Aktif)")
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()
        st.pyplot(fig_r)

    with tab4:
        top_n_m = st.slider("Top N pelanggan pengeluaran tertinggi:", 5, 20, 10, key='rfm_m')
        fig_m, ax_m = plt.subplots(figsize=(10, 4))
        top_m = rfm.sort_values('monetary', ascending=False).head(top_n_m).copy()
        top_m['short_id'] = top_m['customer_unique_id'].str[:10] + '...'
        sns.barplot(data=top_m, x='short_id', y='monetary', palette='Oranges_r', ax=ax_m)
        ax_m.set_xlabel("Customer ID (disingkat)")
        ax_m.set_ylabel("Total Pengeluaran (BRL)")
        ax_m.set_title(f"Top {top_n_m} Pelanggan dengan Pengeluaran Tertinggi")
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()
        st.pyplot(fig_m)

    loyal = (rfm['frequency'] > 1).sum()
    high_spender = top_5_customers.iloc[0]['customer_unique_id'][:12] + '...' if len(top_5_customers) > 0 else '-'
    st.info(
        f"💡 **Insight:** Terdapat **{len(top_5_customers):,} pelanggan** dalam segmen Top 5% (Champions) "
        f"dengan skor RFM ≥ {top_5_threshold:.0f}. "
        f"Sebanyak **{loyal:,} pelanggan** melakukan lebih dari 1 pesanan — segmen loyal yang perlu "
        f"dipertahankan melalui program reward eksklusif. "
        f"Rata-rata recency **{rfm['recency'].mean():.0f} hari** menunjukkan seberapa aktif basis pelanggan saat ini."
    )
else:
    st.warning("Tidak ada data transaksi pada rentang tanggal yang dipilih.")

st.markdown("---")

# ==========================================
# 4. Volume Transaksi Berdasarkan Wilayah
# ==========================================
st.subheader("🗺️ Volume Transaksi per Wilayah (State)")

top_n_state = st.slider("Tampilkan Top N Wilayah:", min_value=5, max_value=27, value=10, step=1)

if not filtered_orders.empty:
    filtered_customers = customers[customers['customer_id'].isin(filtered_orders['customer_id'])].copy()

    state_volume = (
        filtered_customers['customer_state']
        .value_counts()
        .reset_index()
    )
    state_volume.columns = ['customer_state', 'transaction_count']
    top_states = state_volume.head(top_n_state)

    fig4, ax4 = plt.subplots(figsize=(12, 5))
    bars = sns.barplot(data=top_states, x='customer_state', y='transaction_count', palette='magma', ax=ax4)
    max_val = top_states['transaction_count'].max()
    for bar, val in zip(bars.patches, top_states['transaction_count']):
        ax4.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + max_val * 0.01,
                 f'{val:,}', ha='center', va='bottom', fontsize=8)
    ax4.set_xlabel("Kode State")
    ax4.set_ylabel("Jumlah Transaksi")
    plt.xticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig4)

    # Keterangan kode state yang tampil — 3 kolom
    st.markdown("**Keterangan Kode State:**")
    displayed_codes = top_states['customer_state'].tolist()
    cols = st.columns(3)
    for i, code in enumerate(displayed_codes):
        cols[i % 3].markdown(f"• **{code}** = {STATE_NAMES.get(code, code)}")

    # Insight
    top1_state = top_states.iloc[0]['customer_state']
    top1_count = top_states.iloc[0]['transaction_count']
    top1_name = STATE_NAMES.get(top1_state, top1_state)
    top2_state = top_states.iloc[1]['customer_state'] if len(top_states) > 1 else "-"
    top2_name = STATE_NAMES.get(top2_state, top2_state)
    total_all = state_volume['transaction_count'].sum()
    pct_top1 = top1_count / total_all * 100 if total_all > 0 else 0

    st.info(
        f"💡 **Insight:** **{top1_state} ({top1_name})** mendominasi transaksi dengan **{top1_count:,} pesanan** "
        f"({pct_top1:.1f}% dari total), diikuti **{top2_state} ({top2_name})**. "
        f"Strategi *Hub-and-Spoke* sangat cocok diterapkan di wilayah dengan volume tinggi untuk "
        f"efisiensi logistik dan pengiriman."
    )
else:
    st.warning("Tidak ada data pelanggan pada rentang tanggal yang dipilih.")