// Global application state
const state = {
    rules: {},
    credentials: {},
    suggestions: [],
    history: [],
    selectedProfile: "",
    activeTab: "pending", // pending or history
    region: "na",
    dashboardMode: "seller", // seller or kindle
    charts: {
        trend: null,
        budget: null
    }
};

// Initialize Application on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
    // Sync document theme immediately to body
    if (document.documentElement.classList.contains("light-theme")) {
        document.body.classList.add("light-theme");
    }

    // Lucide Icons Render
    lucide.createIcons();

    // Init Theme Toggle
    initThemeToggle();

    // Init Slider Listeners
    initSliders();

    // Init Drag & Drop Uploader
    initUploader();

    // Init Date range selectors
    initDateSelectors();

    // Load Initial Data
    loadRules();
    loadCredentials();
    loadMetrics();
    loadHistory();
    loadSuggestions(true);

    // Setup action buttons
    document.getElementById("api-optimize-btn").addEventListener("click", runApiOptimization);
    document.getElementById("save-rules-btn").addEventListener("click", saveRules);
    document.getElementById("save-credentials-btn").addEventListener("click", saveCredentials);
    document.getElementById("apply-selected-btn").addEventListener("click", applySelectedRecommendations);
    document.getElementById("select-all-checkbox").addEventListener("change", toggleSelectAll);
    document.getElementById("profile-selector").addEventListener("change", selectProfile);

    // Hide KDP bottom tab since it is now controlled by the top mode switcher
    if (document.getElementById("btn-tab-kindle")) {
        document.getElementById("btn-tab-kindle").style.display = "none";
    }
});

// --- THEME MANAGEMENT UTILITIES ---

function getThemeColors() {
    const isLight = document.body.classList.contains("light-theme");
    return {
        text: isLight ? '#475569' : '#9ca3af',
        grid: isLight ? 'rgba(15, 23, 42, 0.05)' : 'rgba(255, 255, 255, 0.03)',
        border: isLight ? '#ffffff' : '#121427'
    };
}

function initThemeToggle() {
    const btn = document.getElementById("theme-toggle-btn");
    if (!btn) return;

    btn.addEventListener("click", () => {
        const doc = document.documentElement;
        const body = document.body;
        
        if (doc.classList.contains("light-theme")) {
            doc.classList.remove("light-theme");
            body.classList.remove("light-theme");
            try {
                localStorage.setItem("theme", "dark");
            } catch (e) {
                console.warn("Could not save theme preference:", e);
            }
        } else {
            doc.classList.add("light-theme");
            body.classList.add("light-theme");
            try {
                localStorage.setItem("theme", "light");
            } catch (e) {
                console.warn("Could not save theme preference:", e);
            }
        }
        
        updateThemeToggleUI();
        
        // Re-load metrics to re-render charts with appropriate theme colors
        loadMetrics();
    });

    updateThemeToggleUI();
}

function updateThemeToggleUI() {
    const isLight = document.documentElement.classList.contains("light-theme");
    const icon = document.getElementById("theme-toggle-icon");
    if (!icon) return;

    if (isLight) {
        icon.setAttribute("data-lucide", "moon");
        icon.className = "w-5 h-5 text-slate-700 hover:text-indigo-600 transition-all duration-300";
    } else {
        icon.setAttribute("data-lucide", "sun");
        icon.className = "w-5 h-5 text-gray-300 hover:text-cyan-400 transition-all duration-300";
    }

    if (window.lucide) {
        window.lucide.createIcons();
    }
}

// --- DATE RANGE MANAGEMENT UTILITIES ---

function getSelectedDateParams() {
    const selector = document.getElementById("date-range-selector");
    if (!selector) return "";

    const value = selector.value;
    if (value === "custom") {
        const start = document.getElementById("start-date").value;
        const end = document.getElementById("end-date").value;
        if (start && end) {
            return `start_date=${start}&end_date=${end}&range_type=custom`;
        }
        return "";
    }
    return `range_type=${value}`;
}

function initDateSelectors() {
    const selector = document.getElementById("date-range-selector");
    const container = document.getElementById("custom-date-container");
    const startInput = document.getElementById("start-date");
    const endInput = document.getElementById("end-date");
    if (!selector) return;

    // Set default dates: full year 2026
    if (startInput && !startInput.value) {
        startInput.value = "2026-01-01";
    }
    if (endInput && !endInput.value) {
        endInput.value = "2026-12-31";
    }

    selector.addEventListener("change", () => {
        if (selector.value === "custom") {
            container.classList.remove("hidden");
        } else {
            container.classList.add("hidden");
            // Reload dashboard metrics & optimization recommendations
            loadMetrics();
            if (state.suggestions && state.suggestions.length > 0) {
                runApiOptimization();
            }
        }
    });

    const onDateChange = () => {
        const start = startInput.value;
        const end = endInput.value;
        if (start && end) {
            loadMetrics();
            if (state.suggestions && state.suggestions.length > 0) {
                runApiOptimization();
            }
        }
    };

    if (startInput) startInput.addEventListener("change", onDateChange);
    if (endInput) endInput.addEventListener("change", onDateChange);
}

// --- CORE UTILITIES & METRICS LOADERS ---

async function loadMetrics() {
    try {
        const params = getSelectedDateParams();
        const modeParam = state.dashboardMode ? `mode=${state.dashboardMode}` : "";
        const combinedParams = [params, modeParam].filter(Boolean).join("&");
        const query = combinedParams ? `?${combinedParams}` : "";
        const res = await fetch(`/api/campaigns/metrics${query}`);
        const data = await res.json();

        // Populate Cards
        if (document.getElementById("metric-global-sales")) {
            document.getElementById("metric-global-sales").innerText = `$${data.global_sales.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN`;
        }
        if (document.getElementById("metric-sales")) {
            document.getElementById("metric-sales").innerText = `$${data.sales.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN`;
        }
        if (document.getElementById("metric-organic-sales")) {
            document.getElementById("metric-organic-sales").innerText = `$${data.organic_sales.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN`;
        }
        if (document.getElementById("metric-spend")) {
            document.getElementById("metric-spend").innerText = `$${data.spend.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN`;
        }
        if (document.getElementById("metric-acos")) {
            document.getElementById("metric-acos").innerText = `${(data.acos * 100).toFixed(1)}%`;
        }
        if (document.getElementById("metric-tacos")) {
            document.getElementById("metric-tacos").innerText = `${(data.tacos * 100).toFixed(1)}%`;
        }
        if (document.getElementById("metric-roas")) {
            document.getElementById("metric-roas").innerText = `${data.global_roas.toFixed(2)}x`;
        }
        if (document.getElementById("metric-conversion")) {
            document.getElementById("metric-conversion").innerText = `${(data.conversion_rate * 100).toFixed(1)}%`;
        }

        // Populate Financial Breakdown Widget
        if (document.getElementById("financial-gross-sales")) {
            document.getElementById("financial-gross-sales").innerText = `$${data.global_sales.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN`;
        }
        if (document.getElementById("financial-referral-fee")) {
            document.getElementById("financial-referral-fee").innerText = `-$${data.referral_fee.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN`;
        }
        if (document.getElementById("financial-fba-fee")) {
            document.getElementById("financial-fba-fee").innerText = `-$${data.fba_fee.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN`;
        }
        if (document.getElementById("financial-tax-retention")) {
            document.getElementById("financial-tax-retention").innerText = `-$${data.tax_retention.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN`;
        }
        if (document.getElementById("financial-ads-spend")) {
            document.getElementById("financial-ads-spend").innerText = `-$${data.spend.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN`;
        }
        if (document.getElementById("financial-net-payout")) {
            document.getElementById("financial-net-payout").innerText = `$${data.net_payout.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN`;
        }

        // Populate Seller Central Summary Widget
        if (document.getElementById("seller-balance")) {
            document.getElementById("seller-balance").innerText = `$${data.saldo_total.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN`;
        }
        if (document.getElementById("seller-pending-orders")) {
            document.getElementById("seller-pending-orders").innerText = data.pending_orders;
        }
        if (document.getElementById("seller-buy-box")) {
            document.getElementById("seller-buy-box").innerText = `${(data.buy_box_pct * 100).toFixed(0)}%`;
        }
        if (document.getElementById("seller-promotions")) {
            document.getElementById("seller-promotions").innerText = `$${data.ventas_promociones.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN`;
        }
        if (document.getElementById("seller-account-status-badge")) {
            const badge = document.getElementById("seller-account-status-badge");
            badge.innerText = `⚠️ ${data.estado_cuenta.toUpperCase()}`;
            if (data.estado_cuenta.toLowerCase() === "en riesgo" || data.estado_cuenta.toLowerCase() === "riesgo") {
                badge.className = "px-2.5 py-1 text-[10px] font-bold rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20";
            } else {
                badge.className = "px-2.5 py-1 text-[10px] font-bold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
                badge.innerText = `✓ SALUDABLE`;
            }
        }

        const acosPill = document.getElementById("acos-status");
        if (acosPill) {
            if (data.acos > 0.35) {
                acosPill.className = "text-rose-400";
                acosPill.innerText = "Alto ACOS";
            } else {
                acosPill.className = "text-emerald-400";
                acosPill.innerText = "Saludable";
            }
        }

        // Render Charts
        initTrendChart(data.daily_trend, data.spend, data.sales);
        initBudgetChart();

        // Render Product & Campaign Breakdown
        loadProductBreakdown();
        loadCampaignBreakdown();
        loadKindleBreakdown();

        if (state.dashboardMode === 'kindle') {
            loadKdpReportStatus();
        }
    } catch (err) {
        console.error("Error loading metrics:", err);
    }
}

window.setDashboardMode = function(mode) {
    state.dashboardMode = mode;
    
    // Toggle active buttons style
    const btnSeller = document.getElementById("btn-mode-seller");
    const btnKindle = document.getElementById("btn-mode-kindle");
    
    if (mode === "seller") {
        btnSeller.className = "px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all duration-300 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20";
        btnKindle.className = "px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all duration-300 text-gray-400 hover:text-gray-200 border-none";
        
        // Update labels to Seller
        document.getElementById("financial-breakdown-title").innerHTML = `<i data-lucide="receipt" class="w-5 h-5 text-emerald-400"></i> Desglose de Tarifas y Retenciones de Amazon`;
        document.getElementById("lbl-gross-sales").innerText = "Ventas Totales (Brutas)";
        document.getElementById("lbl-referral-fee").innerText = "Comisión de Referencia Amazon (15%)";
        document.getElementById("desc-referral-fee").innerText = "Tarifa fija por categoría";
        document.getElementById("lbl-fba-fee").innerText = "Tarifas de Logística de Amazon (FBA)";
        document.getElementById("desc-fba-fee").innerText = "Envío, almacenamiento y manejo estimado ($70 MXN por unidad)";
        document.getElementById("lbl-tax-retention").innerText = "Retenciones de Impuestos (RFC registrado)";
        document.getElementById("desc-tax-retention").innerText = "IVA (8%) + ISR (1%) de ventas brutas";
        document.getElementById("lbl-ads-spend").innerText = "Inversión en Campañas Publicitarias (Ads)";
        document.getElementById("desc-ads-spend").innerText = "Costo de clics y anuncios deducido";
        document.getElementById("financial-payout-title").innerText = "Pago Neto Estimado";
        document.getElementById("lbl-payout-amount").innerText = "Monto a Depositar";
        
        // Update bottom tab buttons
        document.getElementById("btn-tab-products").innerText = "Productos (SKU)";
        document.getElementById("btn-tab-campaigns").innerText = "Campañas (Ads)";
        
        // Hide kindle button and reset to products tab
        if (document.getElementById("btn-tab-kindle")) {
            document.getElementById("btn-tab-kindle").style.display = "none";
        }
        
        // Update uploader texts
        const uploadTitle = document.getElementById("upload-title");
        const uploadDesc = document.getElementById("upload-desc");
        if (uploadTitle) uploadTitle.innerText = "Subir Bulk Sheet o Search Terms";
        if (uploadDesc) uploadDesc.innerText = "Arrastra tu reporte Excel o CSV, o haz clic aquí";
        
        switchTab("products");
    } else {
        btnSeller.className = "px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all duration-300 text-gray-400 hover:text-gray-200 border-none";
        btnKindle.className = "px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all duration-300 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20";
        
        // Update labels to Kindle
        document.getElementById("financial-breakdown-title").innerHTML = `<i data-lucide="receipt" class="w-5 h-5 text-emerald-400"></i> Desglose de Regalías y Costos KDP`;
        document.getElementById("lbl-gross-sales").innerText = "Ventas de Libros (Ventas Ads)";
        document.getElementById("lbl-referral-fee").innerText = "Comisión / Costo de Amazon KDP (32%)";
        document.getElementById("desc-referral-fee").innerText = "Impresión de libros físicos o entrega digital de eBooks";
        document.getElementById("lbl-fba-fee").innerText = "Tarifas de Almacenamiento KDP (0%)";
        document.getElementById("desc-fba-fee").innerText = "KDP no cobra almacenamiento de inventario físico o digital";
        document.getElementById("lbl-tax-retention").innerText = "Retención Fiscal KDP (0%)";
        document.getElementById("desc-tax-retention").innerText = "Retención del 0% por tratado fiscal W-8BEN";
        document.getElementById("lbl-ads-spend").innerText = "Inversión en Publicidad KDP Ads";
        document.getElementById("desc-ads-spend").innerText = "Presupuesto publicitario invertido en campañas";
        document.getElementById("financial-payout-title").innerText = "Ganancia Neta (Regalías Est.)";
        document.getElementById("lbl-payout-amount").innerText = "Regalías Netas Estimadas";
        
        // Update bottom tab buttons
        document.getElementById("btn-tab-products").innerText = "Libros KDP";
        document.getElementById("btn-tab-campaigns").innerText = "Campañas KDP (Ads)";
        
        // Hide kindle button and reset to products (which is Libros KDP now)
        if (document.getElementById("btn-tab-kindle")) {
            document.getElementById("btn-tab-kindle").style.display = "none";
        }
        
        // Update uploader texts
        const uploadTitle = document.getElementById("upload-title");
        const uploadDesc = document.getElementById("upload-desc");
        if (uploadTitle) uploadTitle.innerText = "Subir Reporte KDP, Bulk Sheet o Search Terms";
        if (uploadDesc) uploadDesc.innerText = "Arrastra tu reporte de regalías KDP (Prior Month Royalties/KDP_*), Excel o CSV, o haz clic aquí";
        
        switchTab("products");
    }
    
    // Re-render lucide icons in the title
    if (window.lucide) {
        window.lucide.createIcons();
    }
    
    // Reload credentials, metrics and suggestions for the new mode
    loadCredentials();
    loadMetrics();
    loadSuggestions(true);
};

window.switchTab = function(tabName) {
    const productsView = document.getElementById("products-view");
    const campaignsView = document.getElementById("campaigns-view");
    const kindleView = document.getElementById("kindle-view");
    const btnProducts = document.getElementById("btn-tab-products");
    const btnCampaigns = document.getElementById("btn-tab-campaigns");
    
    if (tabName === 'products') {
        if (state.dashboardMode === 'kindle') {
            productsView.classList.add('hidden');
            campaignsView.classList.add('hidden');
            if (kindleView) kindleView.classList.remove('hidden');
            loadKindleBreakdown();
        } else {
            productsView.classList.remove('hidden');
            campaignsView.classList.add('hidden');
            if (kindleView) kindleView.classList.add('hidden');
        }
        btnProducts.className = "px-4 py-1.5 text-xs font-semibold rounded-lg transition-all duration-300 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20";
        btnCampaigns.className = "px-4 py-1.5 text-xs font-semibold rounded-lg transition-all duration-300 text-gray-400 hover:text-gray-200";
    } else if (tabName === 'campaigns') {
        productsView.classList.add('hidden');
        campaignsView.classList.remove('hidden');
        if (kindleView) kindleView.classList.add('hidden');
        btnProducts.className = "px-4 py-1.5 text-xs font-semibold rounded-lg transition-all duration-300 text-gray-400 hover:text-gray-200";
        btnCampaigns.className = "px-4 py-1.5 text-xs font-semibold rounded-lg transition-all duration-300 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20";
    }
};

async function loadProductBreakdown() {
    try {
        const params = getSelectedDateParams();
        const modeParam = state.dashboardMode ? `mode=${state.dashboardMode}` : "";
        const combinedParams = [params, modeParam].filter(Boolean).join("&");
        const query = combinedParams ? `?${combinedParams}` : "";
        const res = await fetch(`/api/campaigns/products${query}`);
        const products = await res.json();
        
        const tbody = document.getElementById("products-tbody");
        if (!tbody) return;
        tbody.innerHTML = "";
        
        products.forEach(p => {
            const tr = document.createElement("tr");
            tr.className = "border-b border-glassBorder hover:bg-white/[0.01]";
            
            const acosColor = p.acos > 0.35 ? "text-rose-400" : "text-emerald-400";
            const tacosColor = p.tacos > 0.15 ? "text-rose-400" : "text-emerald-400";
            
            let categoryClass = "bg-gray-500/10 text-gray-400 border border-gray-500/20";
            if (p.category === "Digestivo") {
                categoryClass = "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
            } else if (p.category === "Cardiovascular") {
                categoryClass = "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20";
            } else if (p.category === "Balance & Estrés" || p.category.includes("Balance")) {
                categoryClass = "bg-purple-500/10 text-purple-400 border border-purple-500/20";
            }
            
            // Calculate a relative width for quantity sold bar
            const volumePct = Math.min(100, Math.max(10, (p.units / 60) * 100));
            
            tr.innerHTML = `
                <td class="py-4 px-4">
                    <span class="font-mono text-xs text-gray-300 font-semibold">${p.sku}</span>
                    <div class="text-[10px] text-gray-500 font-mono mt-0.5">${p.asin}</div>
                </td>
                <td class="py-4 px-4">
                    <div class="font-semibold text-gray-100">${p.name}</div>
                </td>
                <td class="py-4 px-4 text-center">
                    <span class="px-2.5 py-1 text-[10px] font-bold rounded-full ${categoryClass}">${p.category}</span>
                </td>
                <td class="py-4 px-4 text-center">
                    <div class="font-medium">${p.units}</div>
                    <div class="w-16 bg-white/5 h-1 rounded overflow-hidden mx-auto mt-1.5">
                        <div class="bg-cyan-400 h-full" style="width: ${volumePct}%"></div>
                    </div>
                </td>
                <td class="py-4 px-4 text-center text-gray-300">${p.clicks}</td>
                <td class="py-4 px-4 text-right font-medium">$${p.spend.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</td>
                <td class="py-4 px-4 text-right font-semibold text-cyan-400">$${p.sales.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</td>
                <td class="py-4 px-4 text-right font-semibold text-teal-400">$${p.organic_sales.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</td>
                <td class="py-4 px-4 text-right font-semibold text-emerald-400">$${p.global_sales.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</td>
                <td class="py-4 px-4 text-center font-bold ${acosColor}">${(p.acos * 100).toFixed(1)}%</td>
                <td class="py-4 px-4 text-center font-bold ${tacosColor}">${(p.tacos * 100).toFixed(1)}%</td>
                <td class="py-4 px-4 text-center font-semibold text-cyan-400">${p.roas.toFixed(2)}x</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Error loading product breakdown:", err);
    }
}

async function loadCampaignBreakdown() {
    try {
        const params = getSelectedDateParams();
        const modeParam = state.dashboardMode ? `mode=${state.dashboardMode}` : "";
        const combinedParams = [params, modeParam].filter(Boolean).join("&");
        const query = combinedParams ? `?${combinedParams}` : "";
        const res = await fetch(`/api/campaigns/list${query}`);
        const campaigns = await res.json();
        
        const tbody = document.getElementById("campaigns-tbody");
        if (!tbody) return;
        tbody.innerHTML = "";
        
        campaigns.forEach(c => {
            const tr = document.createElement("tr");
            tr.className = "border-b border-glassBorder hover:bg-white/[0.01]";
            
            const acosColor = c.acos > 0.35 ? "text-rose-400" : "text-emerald-400";
            
            tr.innerHTML = `
                <td class="py-4 px-4 font-semibold text-gray-100">${c.campaign_name}</td>
                <td class="py-4 px-4 text-center"><span class="px-2 py-0.5 text-[10px] font-bold rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 uppercase">${c.adType}</span></td>
                <td class="py-4 px-4 text-right font-medium">$${c.budget.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</td>
                <td class="py-4 px-4 text-center text-gray-300">${c.impressions.toLocaleString('es-MX')}</td>
                <td class="py-4 px-4 text-center text-gray-300">${c.clicks.toLocaleString('es-MX')}</td>
                <td class="py-4 px-4 text-right font-medium">$${c.spend.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</td>
                <td class="py-4 px-4 text-center text-gray-300 font-medium">${c.orders}</td>
                <td class="py-4 px-4 text-right font-semibold text-cyan-400">$${c.sales.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</td>
                <td class="py-4 px-4 text-center font-bold ${acosColor}">${(c.acos * 100).toFixed(1)}%</td>
                <td class="py-4 px-4 text-center font-semibold text-cyan-400">${c.roas.toFixed(2)}x</td>
                <td class="py-4 px-4 text-center font-medium text-teal-400">${(c.cr * 100).toFixed(1)}%</td>
            `;
            tbody.appendChild(tr);
        });
        
        // Update budget chart dynamically with real campaigns data
        state.campaigns = campaigns;
        updateBudgetChart(campaigns);
    } catch (err) {
        console.error("Error loading campaign breakdown:", err);
    }
}

async function loadKindleBreakdown() {
    try {
        const params = getSelectedDateParams();
        const modeParam = state.dashboardMode ? `mode=${state.dashboardMode}` : "";
        const combinedParams = [params, modeParam].filter(Boolean).join("&");
        const query = combinedParams ? `?${combinedParams}` : "";
        const res = await fetch(`/api/campaigns/kindle${query}`);
        const books = await res.json();
        
        const tbody = document.getElementById("kindle-tbody");
        if (!tbody) return;
        tbody.innerHTML = "";
        
        books.forEach(b => {
            const tr = document.createElement("tr");
            tr.className = "border-b border-glassBorder hover:bg-white/[0.01]";
            
            const acosColor = b.acos > 0.50 ? "text-rose-400" : "text-emerald-400";
            const racosColor = b.racos > 0.70 ? "text-rose-400 animate-pulse font-bold" : "text-emerald-400 font-bold";
            const profitColor = b.net_profit >= 0 ? "text-emerald-400 font-bold" : "text-rose-400 font-bold";
            
            let formatClass = "bg-purple-500/10 text-purple-400 border border-purple-500/20";
            if (b.format === "eBook") {
                formatClass = "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20";
            }
            
            tr.innerHTML = `
                <td class="py-4 px-4 font-semibold text-gray-100">
                    <div>${b.title}</div>
                    <div class="text-[10px] text-gray-500 font-mono mt-0.5">${b.asin}</div>
                </td>
                <td class="py-4 px-4 text-center">
                    <span class="px-2.5 py-1 text-[10px] font-bold rounded-full ${formatClass}">${b.format}</span>
                </td>
                <td class="py-4 px-4 text-center text-gray-300">${(b.royalty_pct * 100).toFixed(0)}%</td>
                <td class="py-4 px-4 text-center text-gray-300">$${b.price.toFixed(2)} MXN</td>
                <td class="py-4 px-4 text-center text-gray-300">${b.orders}</td>
                <td class="py-4 px-4 text-center text-gray-300">${b.clicks}</td>
                <td class="py-4 px-4 text-right font-medium">$${b.spend.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</td>
                <td class="py-4 px-4 text-right font-semibold text-cyan-400">$${b.sales.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</td>
                <td class="py-4 px-4 text-right font-semibold text-teal-400">$${b.royalties.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</td>
                <td class="py-4 px-4 text-center font-bold ${acosColor}">${(b.acos * 100).toFixed(1)}%</td>
                <td class="py-4 px-4 text-center font-bold ${racosColor}">${(b.racos * 100).toFixed(1)}%</td>
                <td class="py-4 px-4 text-center font-semibold text-cyan-400">${b.roas.toFixed(2)}x</td>
                <td class="py-4 px-4 text-right font-bold ${profitColor}">$${b.net_profit.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Error loading Kindle KDP breakdown:", err);
    }
}

async function loadKdpReportStatus() {
    try {
        const res = await fetch("/api/campaigns/kdp-report-status");
        const data = await res.json();
        
        const fileInfoEl = document.getElementById("kdp-report-file-info");
        const metricsInfoEl = document.getElementById("kdp-report-metrics-info");
        
        if (!fileInfoEl) return;
        
        if (data.has_report) {
            fileInfoEl.innerText = `Reporte: ${data.filename}`;
            fileInfoEl.title = `Actualizado: ${new Date(data.last_updated).toLocaleString('es-MX')}`;
            fileInfoEl.className = "px-2.5 py-1 rounded-full bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 font-semibold max-w-[250px] truncate";
            
            metricsInfoEl.innerText = `✓ ${data.books_count} libros (${data.total_units} u. / $${data.total_royalties.toLocaleString('es-MX', {minimumFractionDigits:2})} reg.)`;
            metricsInfoEl.classList.remove("hidden");
        } else {
            fileInfoEl.innerText = "Reporte: Ninguno cargado";
            fileInfoEl.className = "px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-gray-300 font-semibold max-w-[250px] truncate";
            metricsInfoEl.classList.add("hidden");
        }
    } catch (err) {
        console.error("Error loading KDP report status:", err);
    }
}

async function loadRules() {
    try {
        const res = await fetch("/api/rules");
        const data = await res.json();
        state.rules = data;

        // Set inputs
        document.getElementById("input-acos").value = Math.round(data.target_acos * 100);
        document.getElementById("input-max-spend").value = data.max_spend_no_sales;
        document.getElementById("input-min-clicks").value = data.min_clicks_no_sales;
        document.getElementById("input-smoothing").value = Math.round(data.smoothing_factor * 10);

        // Update indicators
        updateSliderLabels();
    } catch (err) {
        console.error("Error loading rules:", err);
    }
}

async function saveRules() {
    const acos = parseFloat(document.getElementById("input-acos").value) / 100;
    const maxSpend = parseFloat(document.getElementById("input-max-spend").value);
    const minClicks = parseInt(document.getElementById("input-min-clicks").value);
    const smoothing = parseFloat(document.getElementById("input-smoothing").value) / 10;

    const payload = {
        target_acos: acos,
        max_spend_no_sales: maxSpend,
        min_clicks_no_sales: minClicks,
        smoothing_factor: smoothing,
        min_bid: state.rules.min_bid || 0.02,
        max_bid: state.rules.max_bid || 5.00,
        budget_transfer_pct: state.rules.budget_transfer_pct || 0.15
    };

    try {
        const res = await fetch("/api/rules", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.status === "success") {
            state.rules = data.rules;
            showToast("Reglas de optimización guardadas correctamente.", "success");
        }
    } catch (err) {
        console.error("Error saving rules:", err);
        showToast("Error al guardar reglas.", "error");
    }
}

// Slider labels live update
function initSliders() {
    const sliders = ["input-acos", "input-max-spend", "input-min-clicks", "input-smoothing"];
    sliders.forEach(id => {
        document.getElementById(id).addEventListener("input", updateSliderLabels);
    });
}

function updateSliderLabels() {
    const acosVal = document.getElementById("input-acos").value;
    const maxSpendVal = document.getElementById("input-max-spend").value;
    const minClicksVal = document.getElementById("input-min-clicks").value;
    const smoothingVal = document.getElementById("input-smoothing").value;

    document.getElementById("val-acos").innerText = `${acosVal}%`;
    document.getElementById("val-max-spend").innerText = `$${parseFloat(maxSpendVal).toFixed(2)} MXN`;
    document.getElementById("val-min-clicks").innerText = `${minClicksVal} clics`;
    document.getElementById("val-smoothing").innerText = `${(parseFloat(smoothingVal) / 10).toFixed(1)}`;
}

// --- CREDENTIALS MANAGEMENT (LWA FLOW) ---

async function loadCredentials() {
    try {
        const modeParam = state.dashboardMode ? `mode=${state.dashboardMode}` : "";
        const query = modeParam ? `?${modeParam}` : "";
        const res = await fetch(`/api/auth/credentials${query}`);
        const creds = await res.json();
        state.credentials = creds;

        const modeText = document.getElementById("mode-text");
        const modePill = document.getElementById("status-mode-pill");
        
        if (creds.configured) {
            document.getElementById("input-client-id").value = creds.client_id;
            document.getElementById("input-client-id").placeholder = "amzn1.application-oa2-client.xxxxx";
            document.getElementById("input-client-secret").value = "";
            document.getElementById("input-client-secret").placeholder = "•••••••••••••••••••••••••••• (Configurado)";
            document.getElementById("input-refresh-token").value = "";
            document.getElementById("input-refresh-token").placeholder = "Atzr|•••••••••••••••••••••••••••• (Configurado)";

            if (creds.mode === "live") {
                modeText.innerText = "Modo Live API";
                modePill.className = "flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-950/50 border border-emerald-500/30 text-xs font-semibold text-emerald-400";
                modePill.querySelector("span").className = "w-2 h-2 rounded-full bg-emerald-400 animate-pulse";
            } else {
                modeText.innerText = "Modo Simulado";
                modePill.className = "flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-950/50 border border-cyan-500/30 text-xs font-semibold text-cyan-400";
                modePill.querySelector("span").className = "w-2 h-2 rounded-full bg-cyan-400 animate-ping";
            }
            setRegion(creds.region);
            loadProfiles();
        } else {
            document.getElementById("input-client-id").value = "";
            document.getElementById("input-client-id").placeholder = "amzn1.application-oa2-client.xxxxx";
            document.getElementById("input-client-secret").value = "";
            document.getElementById("input-client-secret").placeholder = "••••••••••••••••••••••••••••";
            document.getElementById("input-refresh-token").value = "";
            document.getElementById("input-refresh-token").placeholder = "Atzr|xxxxx...";

            modeText.innerText = "Modo Simulación (Sin API)";
            modePill.className = "flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-orange-950/50 border border-orange-500/30 text-xs font-semibold text-orange-400";
            modePill.querySelector("span").className = "w-2 h-2 rounded-full bg-orange-400 animate-pulse";
            loadProfiles();
        }
    } catch (err) {
        console.error("Error loading credentials:", err);
    }
}

async function loadProfiles() {
    try {
        const modeParam = state.dashboardMode ? `mode=${state.dashboardMode}` : "";
        const query = modeParam ? `?${modeParam}` : "";
        const res = await fetch(`/api/auth/profiles${query}`);
        if (res.status === 200) {
            const profiles = await res.json();
            const selector = document.getElementById("profile-selector");
            selector.innerHTML = "";
            
            if (profiles.length === 0) {
                selector.innerHTML = `<option value="">No hay perfiles</option>`;
                return;
            }
            
            profiles.forEach(p => {
                const opt = document.createElement("option");
                opt.value = p.profileId;
                opt.innerText = `${p.accountInfo.name} (${p.countryCode})`;
                if (p.profileId === state.credentials.profile_id) {
                    opt.selected = true;
                    state.selectedProfile = p.profileId;
                }
                selector.appendChild(opt);
            });
        }
    } catch (err) {
        console.error("Error loading profiles:", err);
    }
}

async function selectProfile() {
    const profileId = document.getElementById("profile-selector").value;
    if (!profileId) return;
    
    try {
        const modeParam = state.dashboardMode ? `mode=${state.dashboardMode}` : "";
        const query = modeParam ? `?${modeParam}` : "";
        const res = await fetch(`/api/auth/select-profile${query}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ profile_id: profileId })
        });
        const data = await res.json();
        if (data.status === "success") {
            state.selectedProfile = profileId;
            showToast(`Perfil activo cambiado: ${profileId}`, "success");
            loadMetrics();
        }
    } catch (err) {
        console.error("Error selecting profile:", err);
    }
}

function setRegion(reg) {
    state.region = reg;
    ["na", "eu", "fe"].forEach(r => {
        const btn = document.getElementById(`btn-reg-${r}`);
        if (r === reg) {
            btn.className = "py-2.5 px-3 rounded-xl border border-cyan-400 bg-cyan-950/20 text-cyan-400 font-bold text-xs text-center transition-all";
        } else {
            btn.className = "py-2.5 px-3 rounded-xl border border-white/5 bg-white/5 text-gray-400 font-bold text-xs text-center transition-all";
        }
    });
}

async function saveCredentials() {
    const clientId = document.getElementById("input-client-id").value;
    const clientSecret = document.getElementById("input-client-secret").value;
    const refreshToken = document.getElementById("input-refresh-token").value;
    
    const alert = document.getElementById("auth-alert");

    // If client ID is masked and other fields are empty, do not re-save
    if (clientId.includes("...") && !clientSecret && !refreshToken) {
        alert.className = "p-3 rounded-xl border border-rose-500/20 bg-rose-950/10 text-rose-400 text-xs";
        alert.innerHTML = `✗ Las credenciales ya están configuradas y guardadas para este modo. Para modificarlas o actualizarlas, introduce los campos completos. De lo contrario, haz clic en Cancelar.`;
        alert.classList.remove("hidden");
        return;
    }
    
    const payload = {
        client_id: clientId,
        client_secret: clientSecret,
        refresh_token: refreshToken,
        region: state.region
    };

    alert.className = "p-3 rounded-xl border border-cyan-500/20 bg-cyan-950/10 text-cyan-400 text-xs flex items-center gap-2";
    alert.innerHTML = `<i data-lucide="loader" class="w-4 h-4 animate-spin"></i> Validando credenciales con Amazon Ads...`;
    alert.classList.remove("hidden");
    lucide.createIcons();

    try {
        const modeParam = state.dashboardMode ? `mode=${state.dashboardMode}` : "";
        const query = modeParam ? `?${modeParam}` : "";
        const res = await fetch(`/api/auth/credentials${query}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        if (res.status === 200) {
            alert.className = "p-3 rounded-xl border border-emerald-500/20 bg-emerald-950/10 text-emerald-400 text-xs";
            alert.innerHTML = `✓ ${data.message}`;
            showToast("Credenciales de API guardadas correctamente.", "success");
            setTimeout(() => {
                toggleCredentialsPanel(false);
                loadCredentials();
            }, 1500);
        } else {
            throw new Error(data.detail || "Authentication validation failed.");
        }
    } catch (err) {
        alert.className = "p-3 rounded-xl border border-rose-500/20 bg-rose-950/10 text-rose-400 text-xs";
        alert.innerHTML = `✗ Error: ${err.message}`;
        showToast("Error de conexión con la API de Amazon Ads.", "error");
    }
}

function toggleCredentialsPanel(open) {
    const panel = document.getElementById("credentials-panel");
    const alert = document.getElementById("auth-alert");
    if (open) {
        panel.classList.add("show");
    } else {
        panel.classList.remove("show");
        alert.classList.add("hidden");
    }
}

// --- OPTIMIZATION LOGIC & API TRIGGERS ---

async function loadSuggestions(cachedOnly = false) {
    try {
        const params = getSelectedDateParams();
        const modeParam = state.dashboardMode ? `mode=${state.dashboardMode}` : "";
        let combinedParts = [params, modeParam].filter(Boolean);
        if (cachedOnly) {
            combinedParts.push("cached=true");
        }
        const query = combinedParts.length > 0 ? `?${combinedParts.join("&")}` : "";
        const res = await fetch(`/api/campaigns/suggestions${query}`);
        const suggestions = await res.json();
        state.suggestions = suggestions;
        populateSuggestionsTable(suggestions);
        return suggestions;
    } catch (err) {
        console.error("Error loading suggestions:", err);
        throw err;
    }
}

async function runApiOptimization() {
    const apiBtn = document.getElementById("api-optimize-btn");
    apiBtn.disabled = true;
    apiBtn.innerHTML = `<i data-lucide="loader" class="w-4 h-4 animate-spin"></i> Calculando...`;
    lucide.createIcons();
    
    try {
        const suggestions = await loadSuggestions(false);
        
        // Show bulk processed container as hidden since we processed via API
        document.getElementById("download-sheet-container").classList.add("hidden");
        
        showToast(`Se han generado ${suggestions.length} recomendaciones de optimización.`, "success");
    } catch (err) {
        showToast("Error al obtener recomendaciones de la API.", "error");
    } finally {
        apiBtn.disabled = false;
        apiBtn.innerHTML = `<i data-lucide="refresh-cw" class="w-4 h-4"></i> Ejecutar Optimización API`;
        lucide.createIcons();
    }
}

function populateSuggestionsTable(suggestions) {
    const tbody = document.getElementById("recommendations-tbody");
    tbody.innerHTML = "";
    
    if (suggestions.length === 0) {
        tbody.innerHTML = `
        <tr id="table-empty-state">
            <td colspan="7" class="py-20 text-center text-gray-400">
                <div class="flex flex-col items-center gap-3">
                    <div class="p-4 bg-white/5 rounded-full text-gray-500 border border-white/5">
                        <i data-lucide="inbox" class="w-8 h-8"></i>
                    </div>
                    <h5 class="text-sm font-semibold text-gray-300">No hay recomendaciones</h5>
                    <p class="text-xs max-w-sm">Ejecuta la optimización API o sube un archivo Excel de reportes para ver sugerencias aquí.</p>
                </div>
            </td>
        </tr>`;
        lucide.createIcons();
        return;
    }
    
    suggestions.forEach(s => {
        const tr = document.createElement("tr");
        tr.className = "border-b border-glassBorder hover:bg-white/[0.01]";
        
        // Define badge style
        let badgeType = "";
        let badgeLabel = "";
        if (s.recommendation_type === "BID_ADJUSTMENT") {
            badgeType = "badge-bid";
            badgeLabel = "Pujas";
        } else if (s.recommendation_type === "NEGATIVIZATION") {
            badgeType = "badge-negative";
            badgeLabel = "Negativo";
        } else if (s.recommendation_type === "BUDGET_REDISTRIBUTION") {
            badgeType = "badge-budget";
            badgeLabel = "Presupuesto";
        } else if (s.recommendation_type === "KEYWORD_HARVESTING") {
            badgeType = "badge-harvest";
            badgeLabel = "Sembrar";
        }
        
        tr.innerHTML = `
            <td class="py-4 px-5 text-center">
                <input type="checkbox" name="recommendation-checkbox" value="${s.id}" checked class="w-4 h-4 rounded accent-cyan-400 cursor-pointer">
            </td>
            <td class="py-4 px-4 font-semibold text-gray-200">
                <div>${s.campaign_name}</div>
                <div class="text-[10px] text-gray-400">${s.ad_group_name}</div>
            </td>
            <td class="py-4 px-4 text-xs font-mono text-gray-300">${s.keyword_text} <span class="text-gray-500">(${s.match_type})</span></td>
            <td class="py-4 px-4">
                <span class="badge ${badgeType}">${badgeLabel}</span>
            </td>
            <td class="py-4 px-4 text-center text-xs text-gray-400 font-semibold">
                ${(s.recommendation_type === 'NEGATIVIZATION' || s.recommendation_type === 'KEYWORD_HARVESTING') ? 'N/A' : `$${s.current_value.toFixed(2)} MXN`}
            </td>
            <td class="py-4 px-4 text-center text-xs text-cyan-400 font-bold">
                ${s.recommendation_type === 'NEGATIVIZATION' ? 'Neg. Exact' : (s.recommendation_type === 'KEYWORD_HARVESTING' ? `Exact: $${s.recommended_value.toFixed(2)} MXN` : `$${s.recommended_value.toFixed(2)} MXN`)}
            </td>
            <td class="py-4 px-4 text-xs text-gray-300 max-w-xs leading-relaxed">${s.reason}</td>
        `;
        tbody.appendChild(tr);
    });
}

function toggleSelectAll() {
    const isChecked = document.getElementById("select-all-checkbox").checked;
    const checkboxes = document.getElementsByName("recommendation-checkbox");
    checkboxes.forEach(cb => cb.checked = isChecked);
}

async function applySelectedRecommendations() {
    const checkboxes = document.getElementsByName("recommendation-checkbox");
    const ids = [];
    checkboxes.forEach(cb => {
        if (cb.checked) ids.push(parseInt(cb.value));
    });
    
    if (ids.length === 0) {
        showToast("Selecciona al menos una recomendación para aplicar.", "error");
        return;
    }
    
    const applyBtn = document.getElementById("apply-selected-btn");
    applyBtn.disabled = true;
    applyBtn.innerHTML = `<i data-lucide="loader" class="w-3.5 h-3.5 animate-spin"></i> Aplicando...`;
    lucide.createIcons();
    
    // Choose endpoint based on recommendations sources
    const isBulk = state.suggestions.some(s => s.source.endsWith(".xlsx") || s.source.endsWith(".csv"));
    const endpoint = isBulk ? "/api/bulk/apply-bulk-cache" : "/api/campaigns/apply";

    try {
        const modeParam = state.dashboardMode ? `mode=${state.dashboardMode}` : "";
        const query = modeParam ? `?${modeParam}` : "";
        const res = await fetch(`${endpoint}${query}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ suggestion_ids: ids })
        });
        const data = await res.json();
        
        if (data.status === "success") {
            showToast(`✓ Se aplicaron ${data.applied_count} optimizaciones exitosamente.`, "success");
            // Clear or update table
            state.suggestions = state.suggestions.filter(s => !ids.includes(s.id));
            populateSuggestionsTable(state.suggestions);
            loadMetrics();
            loadHistory();
        }
    } catch (err) {
        console.error("Error applying updates:", err);
        showToast("Error al aplicar recomendaciones.", "error");
    } finally {
        applyBtn.disabled = false;
        applyBtn.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5"></i> Aplicar recomendaciones seleccionadas`;
        lucide.createIcons();
    }
}

// --- FILE UPLOAD (BULK MANAGER) ---

function initUploader() {
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    
    // Trigger file selection on click
    dropZone.addEventListener("click", () => fileInput.click());
    
    // Handle file selection
    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
    
    // Drag events
    ["dragenter", "dragover"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.add("border-cyan-400", "bg-cyan-500/[0.04]");
        }, false);
    });
    
    ["dragleave", "drop"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.remove("border-cyan-400", "bg-cyan-500/[0.04]");
        }, false);
    });
    
    dropZone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });
}

async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append("file", file);
    
    const nameLower = file.name.toLowerCase();
    const isKdpReport = nameLower.includes("prior_month") || nameLower.includes("kdp_") || nameLower.includes("royalt") || nameLower.includes("regal");
    const isSearchTerm = nameLower.includes("search") || nameLower.includes("term") || nameLower.includes("busqueda");
    
    // KDP reports are handled by the backend automatically in bulk-sheet endpoint
    const endpoint = isKdpReport ? "/api/bulk/upload-bulk-sheet" : (isSearchTerm ? "/api/bulk/upload-search-terms" : "/api/bulk/upload-bulk-sheet");
    
    // Show progress loader
    const progressContainer = document.getElementById("upload-progress-container");
    const filenameEl = document.getElementById("upload-filename");
    const pctEl = document.getElementById("upload-pct");
    const progressBar = document.getElementById("upload-progress-bar");
    
    filenameEl.innerText = file.name;
    pctEl.innerText = "0%";
    progressBar.style.width = "0%";
    progressContainer.classList.remove("hidden");
    
    // Fake progress simulation for UX
    let progress = 0;
    const interval = setInterval(() => {
        if (progress < 90) {
            progress += 15;
            pctEl.innerText = `${progress}%`;
            progressBar.style.width = `${progress}%`;
        }
    }, 150);
    
    try {
        const res = await fetch(endpoint, {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        
        clearInterval(interval);
        pctEl.innerText = "100%";
        progressBar.style.width = "100%";
        
        if (res.status === 200) {
            showToast("✓ Archivo procesado correctamente.", "success");
            
            if (data.file_type === "kdp_royalty_report") {
                showToast(`✓ ${data.message || "Reporte de regalías KDP cargado correctamente."}`, "success");
                await loadKdpReportStatus();
                await loadMetrics();
                await loadKindleBreakdown();
            } else if (data.file_type === "seller_business_report") {
                showToast("✓ Reporte de Seller Central cargado. Actualizando métricas...", "success");
                await loadMetrics();
                await loadProductBreakdown();
                await loadCampaignBreakdown();
            } else {
                state.suggestions = data.suggestions;
                populateSuggestionsTable(data.suggestions);
                
                // Set download file link if Bulk Sheet uploader
                if (data.download_url) {
                    const downloadContainer = document.getElementById("download-sheet-container");
                    const downloadBtn = document.getElementById("download-sheet-btn");
                    downloadBtn.href = data.download_url;
                    downloadContainer.classList.remove("hidden");
                } else {
                    document.getElementById("download-sheet-container").classList.add("hidden");
                }
            }
        } else {
            throw new Error(data.detail || "Error processing file upload.");
        }
    } catch (err) {
        clearInterval(interval);
        progressContainer.classList.add("hidden");
        console.error("Upload error:", err);
        showToast(err.message, "error");
    } finally {
        setTimeout(() => {
            progressContainer.classList.add("hidden");
        }, 3000);
    }
}

// --- OPTIMIZATION LOG / HISTORY TAB ---

async function loadHistory() {
    try {
        const res = await fetch("/api/history");
        const data = await res.json();
        state.history = data;
        
        populateHistoryTable(data);
    } catch (err) {
        console.error("Error loading history:", err);
    }
}

function populateHistoryTable(history) {
    const tbody = document.getElementById("history-tbody");
    tbody.innerHTML = "";
    
    if (history.length === 0) {
        tbody.innerHTML = `
        <tr>
            <td colspan="6" class="py-12 text-center text-gray-500 text-xs">
                No hay historial de optimización registrado todavía.
            </td>
        </tr>`;
        return;
    }
    
    history.forEach(h => {
        const tr = document.createElement("tr");
        tr.className = "border-b border-glassBorder hover:bg-white/[0.01]";
        
        // Format ISO Date
        const date = new Date(h.timestamp);
        const formattedDate = date.toLocaleString('es-ES', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
        
        tr.innerHTML = `
            <td class="py-4 px-5 font-semibold text-gray-300">${formattedDate}</td>
            <td class="py-4 px-4 text-xs font-mono text-cyan-400">${h.type}</td>
            <td class="py-4 px-4 text-center font-bold text-gray-200">${h.keywords_updated}</td>
            <td class="py-4 px-4 text-center font-bold text-gray-200">${h.negatives_created}</td>
            <td class="py-4 px-4 text-center font-bold text-gray-200">${h.budgets_redistributed}</td>
            <td class="py-4 px-4 text-xs text-gray-400 max-w-xs truncate" title="${JSON.stringify(h.details)}">
                ACOS Est. ${h.new_acos_est ? (h.new_acos_est * 100).toFixed(1) + '%' : 'N/A'} (Original: ${h.original_acos ? (h.original_acos * 100).toFixed(1) + '%' : 'N/A'})
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function switchSuggestionsTab(tab) {
    state.activeTab = tab;
    const pendingBtn = document.getElementById("tab-pending-btn");
    const historyBtn = document.getElementById("tab-history-btn");
    const recTable = document.getElementById("recommendations-table");
    const histTable = document.getElementById("history-table");
    const applyBtn = document.getElementById("apply-selected-btn");
    const selectAllCheck = document.getElementById("select-all-checkbox");
    
    if (tab === "pending") {
        pendingBtn.className = "pb-1 text-sm font-bold border-b-2 border-cyan-400 text-gray-100 hover:text-white transition-all";
        historyBtn.className = "pb-1 text-sm font-semibold border-b-2 border-transparent text-gray-400 hover:text-gray-200 transition-all";
        recTable.classList.remove("hidden");
        histTable.classList.add("hidden");
        applyBtn.classList.remove("hidden");
        selectAllCheck.disabled = false;
    } else {
        historyBtn.className = "pb-1 text-sm font-bold border-b-2 border-cyan-400 text-gray-100 hover:text-white transition-all";
        pendingBtn.className = "pb-1 text-sm font-semibold border-b-2 border-transparent text-gray-400 hover:text-gray-200 transition-all";
        recTable.classList.add("hidden");
        histTable.classList.remove("hidden");
        applyBtn.classList.add("hidden");
        selectAllCheck.disabled = true;
    }
}

// --- CHARTS INSTANTIATION ---

function initTrendChart(dailyTrend, spendVal, salesVal) {
    const ctx = document.getElementById("metrics-trend-chart").getContext("2d");
    
    // Destroy previous instance
    if (state.charts.trend) state.charts.trend.destroy();
    
    let days = [];
    let spendData = [];
    let salesData = [];
    
    if (dailyTrend && dailyTrend.length > 0) {
        // Sort dailyTrend chronologically by date
        const sortedTrend = [...dailyTrend].sort((a, b) => a.date.localeCompare(b.date));
        days = sortedTrend.map(item => {
            try {
                const parts = item.date.split('-');
                if (parts.length === 3) {
                    return `${parts[2]}/${parts[1]}`; // format as DD/MM
                }
            } catch (e) {}
            return item.date;
        });
        spendData = sortedTrend.map(item => item.spend);
        salesData = sortedTrend.map(item => item.sales);
    } else {
        days = [];
        spendData = [];
        salesData = [];
    }
    
    // Create neon gradients
    const spendGrad = ctx.createLinearGradient(0, 0, 0, 200);
    spendGrad.addColorStop(0, 'rgba(255, 59, 112, 0.25)');
    spendGrad.addColorStop(1, 'rgba(255, 59, 112, 0.00)');
    
    const salesGrad = ctx.createLinearGradient(0, 0, 0, 200);
    salesGrad.addColorStop(0, 'rgba(0, 255, 170, 0.25)');
    salesGrad.addColorStop(1, 'rgba(0, 255, 170, 0.00)');

    const colors = getThemeColors();

    state.charts.trend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: days,
            datasets: [
                {
                    label: 'Ventas ($)',
                    data: salesData.map(v => parseFloat(v.toFixed(2))),
                    borderColor: '#00ffaa',
                    borderWidth: 2,
                    backgroundColor: salesGrad,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 2,
                },
                {
                    label: 'Gasto ($)',
                    data: spendData.map(v => parseFloat(v.toFixed(2))),
                    borderColor: '#ff3b70',
                    borderWidth: 2,
                    backgroundColor: spendGrad,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 2,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: colors.text, font: { family: 'Inter', size: 11 } }
                }
            },
            scales: {
                x: {
                    grid: { color: colors.grid },
                    ticks: { color: colors.text, font: { size: 10 } }
                },
                y: {
                    grid: { color: colors.grid },
                    ticks: { color: colors.text, font: { size: 10 } }
                }
            }
        }
    });
}

function initBudgetChart() {
    updateBudgetChart(state.campaigns || []);
}

function updateBudgetChart(campaigns) {
    const ctx = document.getElementById("budget-doughnut-chart").getContext("2d");
    if (state.charts.budget) state.charts.budget.destroy();
    
    const colors = getThemeColors();
    
    let labels = [];
    let dataValues = [];
    const hasSpend = campaigns && campaigns.some(c => c.spend > 0);
    
    if (campaigns && campaigns.length > 0) {
        labels = campaigns.map(c => c.campaign_name);
        dataValues = campaigns.map(c => hasSpend ? c.spend : c.budget);
    } else {
        labels = ['Sin Campañas'];
        dataValues = [1];
    }
    
    const colorPalette = [
        '#00e1ff', '#6366f1', '#a855f7', '#ec4899', '#f43f5e', 
        '#eab308', '#22c55e', '#3b82f6', '#f97316', '#a8a29e'
    ];
    const bgColors = dataValues.map((_, i) => colorPalette[i % colorPalette.length]);
    
    if (!campaigns || campaigns.length === 0) {
        bgColors[0] = '#475569';
    }

    state.charts.budget = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: dataValues,
                backgroundColor: bgColors,
                borderColor: colors.border,
                borderWidth: 3,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            cutout: '75%'
        }
    });
    
    const legendContainer = document.getElementById("budget-legend-container");
    if (legendContainer) {
        legendContainer.innerHTML = "";
        if (campaigns && campaigns.length > 0) {
            campaigns.forEach((c, idx) => {
                const color = bgColors[idx];
                const span = document.createElement("span");
                span.className = "flex items-center gap-1.5";
                const val = hasSpend ? c.spend : c.budget;
                span.innerHTML = `<span class="w-2.5 h-2.5 rounded-full" style="background-color: ${color}"></span> ${c.campaign_name} ($${val.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN)`;
                legendContainer.appendChild(span);
            });
        } else {
            const span = document.createElement("span");
            span.className = "flex items-center gap-1.5 text-gray-500";
            span.innerHTML = `<span class="w-2.5 h-2.5 rounded-full bg-gray-600"></span> Sin campañas cargadas`;
            legendContainer.appendChild(span);
        }
    }
}

// --- UTILITY TOAST NOTIFICATIONS ---

function showToast(message, type = "success") {
    // Create toast element
    const toast = document.createElement("div");
    toast.className = `fixed bottom-6 right-6 px-5 py-3.5 rounded-2xl shadow-xl backdrop-blur-md border text-sm font-semibold flex items-center gap-3 transition-all duration-300 transform translate-y-12 opacity-0 z-[200]`;
    
    let icon = "info";
    if (type === "success") {
        toast.classList.add("bg-emerald-950/90", "text-emerald-400", "border-emerald-500/30");
        icon = "check-circle";
    } else if (type === "error") {
        toast.classList.add("bg-rose-950/90", "text-rose-400", "border-rose-500/30");
        icon = "alert-circle";
    } else {
        toast.classList.add("bg-indigo-950/90", "text-indigo-400", "border-indigo-500/30");
        icon = "info";
    }
    
    toast.innerHTML = `<i data-lucide="${icon}" class="w-5 h-5 flex-shrink-0"></i> <span>${message}</span>`;
    document.body.appendChild(toast);
    lucide.createIcons();
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove("translate-y-12", "opacity-0");
    }, 100);
    
    // Animate out and remove
    setTimeout(() => {
        toast.classList.add("translate-y-12", "opacity-0");
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
