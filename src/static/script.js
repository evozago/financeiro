// Configuração da API
const API_BASE = '/api';

// Estado da aplicação
let currentPage = 1;
let currentSection = 'dashboard';
let fornecedores = [];
let tiposDespesa = [];

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupNavigation();
    setupForms();
    loadInitialData();
    atualizarDashboard();
}

// Navegação
function setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const section = this.dataset.section;
            showSection(section);
        });
    });
}

function showSection(sectionName) {
    // Atualizar botões de navegação
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');
    
    // Mostrar seção
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionName).classList.add('active');
    
    currentSection = sectionName;
    
    // Carregar dados da seção
    loadSectionData(sectionName);
}

function loadSectionData(section) {
    switch(section) {
        case 'dashboard':
            atualizarDashboard();
            break;
        case 'notas-fiscais':
            buscarNotasFiscais();
            break;
        case 'contas-pagar':
            buscarContasPagar();
            break;
        case 'fornecedores':
            buscarFornecedores();
            break;
        case 'tipos-despesa':
            buscarTiposDespesa();
            break;
    }
}

// Configuração de formulários
function setupForms() {
    // Form upload XML
    document.getElementById('form-upload-xml').addEventListener('submit', handleUploadXML);
    
    // Form conta a pagar
    document.getElementById('form-conta-pagar').addEventListener('submit', handleSalvarContaPagar);
    
    // Form fornecedor
    document.getElementById('form-fornecedor').addEventListener('submit', handleSalvarFornecedor);
    
    // Form tipo de despesa
    document.getElementById('form-tipo-despesa').addEventListener('submit', handleSalvarTipoDespesa);
    
    // Máscara CNPJ
    document.getElementById('fornecedor-cnpj').addEventListener('input', function(e) {
        e.target.value = formatCNPJ(e.target.value);
    });
    
    // Máscara CEP
    document.getElementById('fornecedor-cep').addEventListener('input', function(e) {
        e.target.value = formatCEP(e.target.value);
    });
}

// Carregamento inicial de dados
async function loadInitialData() {
    try {
        await Promise.all([
            carregarFornecedores(),
            carregarTiposDespesa()
        ]);
    } catch (error) {
        console.error('Erro ao carregar dados iniciais:', error);
    }
}

async function carregarFornecedores() {
    try {
        const response = await fetch(`${API_BASE}/fornecedores`);
        const data = await response.json();
        
        if (data.success) {
            fornecedores = data.data;
            populateSelect('conta-fornecedor', fornecedores, 'id', 'razao_social');
            populateSelect('filter-fornecedor', fornecedores, 'id', 'razao_social');
        }
    } catch (error) {
        console.error('Erro ao carregar fornecedores:', error);
    }
}

async function carregarTiposDespesa() {
    try {
        const response = await fetch(`${API_BASE}/tipos-despesa`);
        const data = await response.json();
        
        if (data.success) {
            tiposDespesa = data.data;
            populateSelect('conta-tipo-despesa', tiposDespesa, 'id', 'nome');
        }
    } catch (error) {
        console.error('Erro ao carregar tipos de despesa:', error);
    }
}

function populateSelect(selectId, items, valueField, textField) {
    const select = document.getElementById(selectId);
    if (!select) return;
    
    // Manter primeira opção
    const firstOption = select.querySelector('option');
    select.innerHTML = '';
    if (firstOption) {
        select.appendChild(firstOption);
    }
    
    items.forEach(item => {
        const option = document.createElement('option');
        option.value = item[valueField];
        option.textContent = item[textField];
        select.appendChild(option);
    });
}

// Dashboard
async function atualizarDashboard() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/contas-pagar/dashboard`);
        const data = await response.json();
        
        if (data.success) {
            const dashboard = data.data;
            
            // Atualizar cards
            document.getElementById('total-pendente').textContent = formatCurrency(dashboard.totais.pendente);
            document.getElementById('count-pendente').textContent = `${dashboard.contadores.pendente} contas`;
            
            document.getElementById('total-vencido').textContent = formatCurrency(dashboard.totais.vencido);
            document.getElementById('count-vencido').textContent = `${dashboard.contadores.vencido} contas`;
            
            document.getElementById('total-pago').textContent = formatCurrency(dashboard.totais.pago);
            document.getElementById('count-pago').textContent = `${dashboard.contadores.pago} contas`;
            
            // Atualizar próximos vencimentos
            const tbody = document.getElementById('proximos-vencimentos');
            tbody.innerHTML = '';
            
            if (dashboard.proximos_vencimentos.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">Nenhum vencimento próximo</td></tr>';
            } else {
                dashboard.proximos_vencimentos.forEach(conta => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${conta.fornecedor?.razao_social || 'N/A'}</td>
                        <td>${conta.descricao}</td>
                        <td>${formatDate(conta.data_vencimento)}</td>
                        <td>${formatCurrency(conta.valor_original)}</td>
                        <td><span class="status-badge status-${conta.status.toLowerCase()}">${conta.status}</span></td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        }
    } catch (error) {
        console.error('Erro ao atualizar dashboard:', error);
        showToast('Erro ao carregar dashboard', 'error');
    } finally {
        hideLoading();
    }
}

// Notas Fiscais
async function buscarNotasFiscais(page = 1) {
    showLoading();
    try {
        const search = document.getElementById('search-notas')?.value || '';
        const params = new URLSearchParams({
            page: page,
            per_page: 20,
            search: search
        });
        
        const response = await fetch(`${API_BASE}/notas-fiscais?${params}`);
        const data = await response.json();
        
        if (data.success) {
            renderNotasFiscais(data.data);
            renderPagination('pagination-notas', data.pagination, buscarNotasFiscais);
        }
    } catch (error) {
        console.error('Erro ao buscar notas fiscais:', error);
        showToast('Erro ao carregar notas fiscais', 'error');
    } finally {
        hideLoading();
    }
}

function renderNotasFiscais(notas) {
    const tbody = document.getElementById('lista-notas-fiscais');
    tbody.innerHTML = '';
    
    if (notas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">Nenhuma nota fiscal encontrada</td></tr>';
        return;
    }
    
    notas.forEach(nota => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${nota.numero}/${nota.serie}</td>
            <td>${nota.fornecedor?.razao_social || 'N/A'}</td>
            <td>${formatDate(nota.data_emissao)}</td>
            <td>${formatCurrency(nota.valor_total)}</td>
            <td><span class="status-badge status-${nota.status.toLowerCase()}">${nota.status}</span></td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn view" onclick="visualizarNotaFiscal(${nota.id})" title="Visualizar">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn delete" onclick="excluirNotaFiscal(${nota.id})" title="Excluir">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function handleUploadXML(e) {
    e.preventDefault();
    
    const formData = new FormData();
    const fileInput = document.getElementById('arquivo-xml');
    
    if (!fileInput.files[0]) {
        showToast('Selecione um arquivo XML', 'error');
        return;
    }
    
    formData.append('file', fileInput.files[0]);
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/notas-fiscais/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message, 'success');
            fecharModal('modal-upload-xml');
            document.getElementById('form-upload-xml').reset();
            buscarNotasFiscais();
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        console.error('Erro ao fazer upload:', error);
        showToast('Erro ao processar arquivo XML', 'error');
    } finally {
        hideLoading();
    }
}

// Contas a Pagar
async function buscarContasPagar(page = 1) {
    showLoading();
    try {
        const search = document.getElementById('search-contas')?.value || '';
        const status = document.getElementById('filter-status')?.value || '';
        const fornecedorId = document.getElementById('filter-fornecedor')?.value || '';
        const dataInicio = document.getElementById('filter-data-inicio')?.value || '';
        const dataFim = document.getElementById('filter-data-fim')?.value || '';
        
        const params = new URLSearchParams({
            page: page,
            per_page: 20,
            search: search,
            status: status,
            fornecedor_id: fornecedorId,
            data_inicio: dataInicio,
            data_fim: dataFim
        });
        
        const response = await fetch(`${API_BASE}/contas-pagar?${params}`);
        const data = await response.json();
        
        if (data.success) {
            renderContasPagar(data.data);
            renderPagination('pagination-contas', data.pagination, buscarContasPagar);
        }
    } catch (error) {
        console.error('Erro ao buscar contas a pagar:', error);
        showToast('Erro ao carregar contas a pagar', 'error');
    } finally {
        hideLoading();
    }
}

function renderContasPagar(contas) {
    const tbody = document.getElementById('lista-contas-pagar');
    tbody.innerHTML = '';
    
    if (contas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Nenhuma conta encontrada</td></tr>';
        return;
    }
    
    contas.forEach(conta => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${conta.fornecedor?.razao_social || 'N/A'}</td>
            <td>${conta.descricao}</td>
            <td>${conta.tipo_despesa?.nome || 'N/A'}</td>
            <td>${formatDate(conta.data_vencimento)}</td>
            <td>${formatCurrency(conta.valor_original)}</td>
            <td><span class="status-badge status-${conta.status.toLowerCase()}">${conta.status}</span></td>
            <td>
                <div class="action-buttons">
                    ${conta.status === 'PENDENTE' ? `
                        <button class="action-btn pay" onclick="pagarConta(${conta.id})" title="Pagar">
                            <i class="fas fa-dollar-sign"></i>
                        </button>
                    ` : ''}
                    <button class="action-btn edit" onclick="editarContaPagar(${conta.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete" onclick="excluirContaPagar(${conta.id})" title="Excluir">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function handleSalvarContaPagar(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/contas-pagar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message, 'success');
            fecharModal('modal-conta-pagar');
            document.getElementById('form-conta-pagar').reset();
            buscarContasPagar();
            atualizarDashboard();
        } else {
            showToast(result.error, 'error');
        }
    } catch (error) {
        console.error('Erro ao salvar conta:', error);
        showToast('Erro ao salvar conta a pagar', 'error');
    } finally {
        hideLoading();
    }
}

async function pagarConta(contaId) {
    if (!confirm('Confirma o pagamento desta conta?')) return;
    
    const dataAtual = new Date().toISOString().split('T')[0];
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/contas-pagar/${contaId}/pagar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data_pagamento: dataAtual
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message, 'success');
            buscarContasPagar();
            atualizarDashboard();
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        console.error('Erro ao pagar conta:', error);
        showToast('Erro ao processar pagamento', 'error');
    } finally {
        hideLoading();
    }
}

// Fornecedores
async function buscarFornecedores(page = 1) {
    showLoading();
    try {
        const search = document.getElementById('search-fornecedores')?.value || '';
        const params = new URLSearchParams({
            page: page,
            per_page: 20,
            search: search
        });
        
        const response = await fetch(`${API_BASE}/fornecedores?${params}`);
        const data = await response.json();
        
        if (data.success) {
            renderFornecedores(data.data);
            renderPagination('pagination-fornecedores', data.pagination, buscarFornecedores);
        }
    } catch (error) {
        console.error('Erro ao buscar fornecedores:', error);
        showToast('Erro ao carregar fornecedores', 'error');
    } finally {
        hideLoading();
    }
}

function renderFornecedores(fornecedores) {
    const tbody = document.getElementById('lista-fornecedores');
    tbody.innerHTML = '';
    
    if (fornecedores.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">Nenhum fornecedor encontrado</td></tr>';
        return;
    }
    
    fornecedores.forEach(fornecedor => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${fornecedor.cnpj}</td>
            <td>${fornecedor.razao_social}</td>
            <td>${fornecedor.nome_fantasia || '-'}</td>
            <td>${fornecedor.cidade || '-'}/${fornecedor.uf || '-'}</td>
            <td>${fornecedor.telefone || '-'}</td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn edit" onclick="editarFornecedor(${fornecedor.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete" onclick="excluirFornecedor(${fornecedor.id})" title="Excluir">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function handleSalvarFornecedor(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/fornecedores`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message, 'success');
            fecharModal('modal-fornecedor');
            document.getElementById('form-fornecedor').reset();
            buscarFornecedores();
            carregarFornecedores(); // Atualizar selects
        } else {
            showToast(result.error, 'error');
        }
    } catch (error) {
        console.error('Erro ao salvar fornecedor:', error);
        showToast('Erro ao salvar fornecedor', 'error');
    } finally {
        hideLoading();
    }
}

// Tipos de Despesa
async function buscarTiposDespesa() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/tipos-despesa`);
        const data = await response.json();
        
        if (data.success) {
            renderTiposDespesa(data.data);
        }
    } catch (error) {
        console.error('Erro ao buscar tipos de despesa:', error);
        showToast('Erro ao carregar tipos de despesa', 'error');
    } finally {
        hideLoading();
    }
}

function renderTiposDespesa(tipos) {
    const tbody = document.getElementById('lista-tipos-despesa');
    tbody.innerHTML = '';
    
    if (tipos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center">Nenhum tipo de despesa encontrado</td></tr>';
        return;
    }
    
    tipos.forEach(tipo => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${tipo.nome}</td>
            <td>${tipo.descricao || '-'}</td>
            <td><span class="status-badge ${tipo.ativo ? 'status-pago' : 'status-cancelado'}">${tipo.ativo ? 'Ativo' : 'Inativo'}</span></td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn edit" onclick="editarTipoDespesa(${tipo.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete" onclick="excluirTipoDespesa(${tipo.id})" title="Excluir">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function handleSalvarTipoDespesa(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    data.ativo = document.getElementById('tipo-ativo').checked;
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/tipos-despesa`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message, 'success');
            fecharModal('modal-tipo-despesa');
            document.getElementById('form-tipo-despesa').reset();
            buscarTiposDespesa();
            carregarTiposDespesa(); // Atualizar selects
        } else {
            showToast(result.error, 'error');
        }
    } catch (error) {
        console.error('Erro ao salvar tipo de despesa:', error);
        showToast('Erro ao salvar tipo de despesa', 'error');
    } finally {
        hideLoading();
    }
}

// Modais
function abrirModalUploadXML() {
    document.getElementById('modal-upload-xml').classList.add('active');
}

function abrirModalContaPagar() {
    document.getElementById('modal-conta-pagar').classList.add('active');
}

function abrirModalFornecedor() {
    document.getElementById('modal-fornecedor').classList.add('active');
}

function abrirModalTipoDespesa() {
    document.getElementById('modal-tipo-despesa').classList.add('active');
}

function abrirModalComprovante() {
    showToast('Funcionalidade em desenvolvimento', 'warning');
}

function abrirModalUploadOFX() {
    showToast('Funcionalidade em desenvolvimento', 'warning');
}

function fecharModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Fechar modal clicando fora
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});

// Paginação
function renderPagination(containerId, pagination, callback) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    
    if (pagination.pages <= 1) return;
    
    // Botão anterior
    const prevBtn = document.createElement('button');
    prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
    prevBtn.disabled = !pagination.has_prev;
    prevBtn.onclick = () => callback(pagination.page - 1);
    container.appendChild(prevBtn);
    
    // Páginas
    const startPage = Math.max(1, pagination.page - 2);
    const endPage = Math.min(pagination.pages, pagination.page + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.classList.toggle('active', i === pagination.page);
        pageBtn.onclick = () => callback(i);
        container.appendChild(pageBtn);
    }
    
    // Botão próximo
    const nextBtn = document.createElement('button');
    nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
    nextBtn.disabled = !pagination.has_next;
    nextBtn.onclick = () => callback(pagination.page + 1);
    container.appendChild(nextBtn);
}

// Utilitários
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value || 0);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('pt-BR');
}

function formatCNPJ(value) {
    value = value.replace(/\D/g, '');
    value = value.replace(/^(\d{2})(\d)/, '$1.$2');
    value = value.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
    value = value.replace(/\.(\d{3})(\d)/, '.$1/$2');
    value = value.replace(/(\d{4})(\d)/, '$1-$2');
    return value;
}

function formatCEP(value) {
    value = value.replace(/\D/g, '');
    value = value.replace(/^(\d{5})(\d)/, '$1-$2');
    return value;
}

// Loading
function showLoading() {
    document.getElementById('loading-overlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.remove('active');
}

// Toast Notifications
function showToast(message, type = 'info', title = '') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    const titles = {
        success: 'Sucesso',
        error: 'Erro',
        warning: 'Atenção',
        info: 'Informação'
    };
    
    toast.innerHTML = `
        <i class="toast-icon ${icons[type]}"></i>
        <div class="toast-content">
            <div class="toast-title">${title || titles[type]}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    container.appendChild(toast);
    
    // Auto remove após 5 segundos
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

// Funções de ação (placeholders para funcionalidades futuras)
function visualizarNotaFiscal(id) {
    showToast('Funcionalidade em desenvolvimento', 'warning');
}

function excluirNotaFiscal(id) {
    if (confirm('Confirma a exclusão desta nota fiscal?')) {
        showToast('Funcionalidade em desenvolvimento', 'warning');
    }
}

function editarContaPagar(id) {
    showToast('Funcionalidade em desenvolvimento', 'warning');
}

function excluirContaPagar(id) {
    if (confirm('Confirma a exclusão desta conta a pagar?')) {
        showToast('Funcionalidade em desenvolvimento', 'warning');
    }
}

function editarFornecedor(id) {
    showToast('Funcionalidade em desenvolvimento', 'warning');
}

function excluirFornecedor(id) {
    if (confirm('Confirma a exclusão deste fornecedor?')) {
        showToast('Funcionalidade em desenvolvimento', 'warning');
    }
}

function editarTipoDespesa(id) {
    showToast('Funcionalidade em desenvolvimento', 'warning');
}

function excluirTipoDespesa(id) {
    if (confirm('Confirma a exclusão deste tipo de despesa?')) {
        showToast('Funcionalidade em desenvolvimento', 'warning');
    }
}

