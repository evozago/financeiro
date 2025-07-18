const API_BASE = '/api';

// Estado da aplicação
let currentPage = 1;
let currentSection = 'dashboard';
let fornecedores = [];
let tiposDespesa = [];

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando aplicação...');
    initializeApp();
});

function initializeApp() {
    setupNavigation();
    setupForms();
    setupEventListeners();
    loadInitialData();
    showSection('dashboard');
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
    console.log('Mostrando seção:', sectionName);
    
    // Atualizar botões de navegação
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const activeBtn = document.querySelector(`[data-section="${sectionName}"]`);
    if (activeBtn) activeBtn.classList.add('active');
    
    // Mostrar seção
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    const activeSection = document.getElementById(sectionName);
    if (activeSection) activeSection.classList.add('active');
    
    currentSection = sectionName;
    
    // Carregar dados da seção
    loadSectionData(sectionName);
}

function loadSectionData(section) {
    console.log('Carregando dados da seção:', section);
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
        case 'comprovantes':
            buscarComprovantes();
            break;
        case 'conciliacao':
            buscarExtratosBancarios();
            break;
    }
}

// Event Listeners
function setupEventListeners() {
    // Botões de ação
    document.addEventListener('click', function(e) {
        if (e.target.matches('.btn-nova-conta, [onclick*="abrirModal"]')) {
            const modalId = e.target.dataset.modal || 'modal-conta-pagar';
            abrirModal(modalId);
        }
        
        if (e.target.matches('.btn-importar-xml, [onclick*="importarXML"]')) {
            abrirModal('modal-upload-xml');
        }
        
        if (e.target.matches('.btn-novo-fornecedor')) {
            abrirModal('modal-fornecedor');
        }
        
        if (e.target.matches('.btn-novo-tipo')) {
            abrirModal('modal-tipo-despesa');
        }
        
        if (e.target.matches('.btn-filtrar')) {
            aplicarFiltros();
        }
    });
}

// Configuração de formulários
function setupForms() {
    // Form upload XML
    const formXML = document.getElementById('form-upload-xml');
    if (formXML) {
        formXML.addEventListener('submit', handleUploadXML);
    }
    
    // Form conta a pagar
    const formConta = document.getElementById('form-conta-pagar');
    if (formConta) {
        formConta.addEventListener('submit', handleSalvarContaPagar);
    }
    
    // Form fornecedor
    const formFornecedor = document.getElementById('form-fornecedor');
    if (formFornecedor) {
        formFornecedor.addEventListener('submit', handleSalvarFornecedor);
    }
    
    // Form tipo de despesa
    const formTipo = document.getElementById('form-tipo-despesa');
    if (formTipo) {
        formTipo.addEventListener('submit', handleSalvarTipoDespesa);
    }
}

// Carregamento inicial de dados
async function loadInitialData() {
    console.log('Carregando dados iniciais...');
    try {
        await Promise.all([
            carregarFornecedores(),
            carregarTiposDespesa()
        ]);
        console.log('Dados iniciais carregados com sucesso');
    } catch (error) {
        console.error('Erro ao carregar dados iniciais:', error);
    }
}

async function carregarFornecedores() {
    try {
        console.log('Carregando fornecedores...');
        const response = await fetch(`${API_BASE}/fornecedores`);
        const data = await response.json();
        
        if (data.success) {
            fornecedores = data.data;
            console.log('Fornecedores carregados:', fornecedores.length);
            populateSelect('conta-fornecedor', fornecedores, 'id', 'razao_social');
            populateSelect('filter-fornecedor', fornecedores, 'id', 'razao_social');
        }
    } catch (error) {
        console.error('Erro ao carregar fornecedores:', error);
    }
}

async function carregarTiposDespesa() {
    try {
        console.log('Carregando tipos de despesa...');
        const response = await fetch(`${API_BASE}/tipos-despesa`);
        const data = await response.json();
        
        if (data.success) {
            tiposDespesa = data.data;
            console.log('Tipos de despesa carregados:', tiposDespesa.length);
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
    console.log('Atualizando dashboard...');
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/contas-pagar/dashboard`);
        const data = await response.json();
        
        if (data.success) {
            const dashboard = data.data;
            console.log('Dashboard carregado:', dashboard);
            
            // Atualizar cards
            updateElement('total-pendente', formatCurrency(dashboard.totais.pendente));
            updateElement('count-pendente', `${dashboard.contadores.pendente} contas`);
            
            updateElement('total-vencido', formatCurrency(dashboard.totais.vencido));
            updateElement('count-vencido', `${dashboard.contadores.vencido} contas`);
            
            updateElement('total-pago', formatCurrency(dashboard.totais.pago));
            updateElement('count-pago', `${dashboard.contadores.pago} contas`);
            
            // Atualizar próximos vencimentos
            const tbody = document.getElementById('proximos-vencimentos');
            if (tbody) {
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
        }
    } catch (error) {
        console.error('Erro ao atualizar dashboard:', error);
        showToast('Erro ao carregar dashboard', 'error');
    } finally {
        hideLoading();
    }
}

// Contas a Pagar
async function buscarContasPagar(page = 1) {
    console.log('Buscando contas a pagar...');
    showLoading();
    try {
        const search = getElementValue('search-contas') || '';
        const status = getElementValue('filter-status') || '';
        const fornecedorId = getElementValue('filter-fornecedor') || '';
        const dataInicio = getElementValue('filter-data-inicio') || '';
        const dataFim = getElementValue('filter-data-fim') || '';
        
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
            console.log('Contas a pagar carregadas:', data.data.length);
            renderContasPagar(data.data);
            if (data.pagination) {
                renderPagination('pagination-contas', data.pagination, buscarContasPagar);
            }
        } else {
            console.error('Erro na resposta da API:', data.error);
            showToast(data.error || 'Erro ao carregar contas', 'error');
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
    if (!tbody) {
        console.error('Elemento lista-contas-pagar não encontrado');
        return;
    }
    
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
                            💰
                        </button>
                    ` : ''}
                    <button class="action-btn edit" onclick="editarContaPagar(${conta.id})" title="Editar">
                        ✏️
                    </button>
                    <button class="action-btn delete" onclick="excluirContaPagar(${conta.id})" title="Excluir">
                        🗑️
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Ações das Contas a Pagar
async function pagarConta(contaId) {
    if (!confirm('Confirma o pagamento desta conta?')) return;
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/contas-pagar/${contaId}/pagar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data_pagamento: new Date().toISOString().split('T')[0]
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Conta paga com sucesso!', 'success');
            buscarContasPagar();
            atualizarDashboard();
        } else {
            showToast(result.error || 'Erro ao pagar conta', 'error');
        }
    } catch (error) {
        console.error('Erro ao pagar conta:', error);
        showToast('Erro ao pagar conta', 'error');
    } finally {
        hideLoading();
    }
}

async function editarContaPagar(id) {
    try {
        const response = await fetch(`${API_BASE}/contas-pagar/${id}`);
        const data = await response.json();
        
        if (data.success) {
            const conta = data.data;
            
            // Preencher formulário
            setElementValue('conta-fornecedor', conta.fornecedor_id);
            setElementValue('conta-tipo-despesa', conta.tipo_despesa_id);
            setElementValue('conta-descricao', conta.descricao);
            setElementValue('conta-valor', conta.valor_original);
            setElementValue('conta-vencimento', conta.data_vencimento);
            setElementValue('conta-documento', conta.numero_documento);
            setElementValue('conta-observacoes', conta.observacoes);
            
            // Definir ID para edição
            document.getElementById('form-conta-pagar').dataset.editId = id;
            
            abrirModal('modal-conta-pagar');
        }
    } catch (error) {
        console.error('Erro ao carregar conta:', error);
        showToast('Erro ao carregar dados da conta', 'error');
    }
}

async function excluirContaPagar(id) {
    if (!confirm('Tem certeza que deseja excluir esta conta?')) return;
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/contas-pagar/${id}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Conta excluída com sucesso!', 'success');
            buscarContasPagar();
            atualizarDashboard();
        } else {
            showToast(result.error || 'Erro ao excluir conta', 'error');
        }
    } catch (error) {
        console.error('Erro ao excluir conta:', error);
        showToast('Erro ao excluir conta', 'error');
    } finally {
        hideLoading();
    }
}

// Notas Fiscais
async function buscarNotasFiscais(page = 1) {
    console.log('Buscando notas fiscais...');
    showLoading();
    try {
        const search = getElementValue('search-notas') || '';
        
        const params = new URLSearchParams({
            page: page,
            per_page: 20,
            search: search
        });
        
        const response = await fetch(`${API_BASE}/notas-fiscais?${params}`);
        const data = await response.json();
        
        if (data.success) {
            console.log('Notas fiscais carregadas:', data.data.length);
            renderNotasFiscais(data.data);
            if (data.pagination) {
                renderPagination('pagination-notas', data.pagination, buscarNotasFiscais);
            }
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
    if (!tbody) return;
    
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
                    <button class="action-btn view" onclick="visualizarNota(${nota.id})" title="Visualizar">
                        👁️
                    </button>
                    <button class="action-btn delete" onclick="excluirNota(${nota.id})" title="Excluir">
                        🗑️
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function visualizarNota(id) {
    try {
        const response = await fetch(`${API_BASE}/notas-fiscais/${id}`);
        const data = await response.json();
        
        if (data.success) {
            const nota = data.data;
            
            // Mostrar detalhes da nota em modal
            const modalContent = `
                <h3>Nota Fiscal ${nota.numero}/${nota.serie}</h3>
                <p><strong>Fornecedor:</strong> ${nota.fornecedor?.razao_social}</p>
                <p><strong>Data Emissão:</strong> ${formatDate(nota.data_emissao)}</p>
                <p><strong>Valor Total:</strong> ${formatCurrency(nota.valor_total)}</p>
                <p><strong>Chave de Acesso:</strong> ${nota.chave_acesso}</p>
                <h4>Itens (${nota.itens?.length || 0}):</h4>
                <div style="max-height: 300px; overflow-y: auto;">
                    ${(nota.itens || []).map(item => `
                        <div style="border-bottom: 1px solid #eee; padding: 10px;">
                            <strong>${item.descricao}</strong><br>
                            Qtd: ${item.quantidade} ${item.unidade} - 
                            Valor: ${formatCurrency(item.valor_total)}
                        </div>
                    `).join('')}
                </div>
            `;
            
            showModal('Detalhes da Nota Fiscal', modalContent);
        }
    } catch (error) {
        console.error('Erro ao visualizar nota:', error);
        showToast('Erro ao carregar detalhes da nota', 'error');
    }
}

async function excluirNota(id) {
    if (!confirm('Tem certeza que deseja excluir esta nota fiscal?')) return;
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/notas-fiscais/${id}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Nota fiscal excluída com sucesso!', 'success');
            buscarNotasFiscais();
        } else {
            showToast(result.error || 'Erro ao excluir nota', 'error');
        }
    } catch (error) {
        console.error('Erro ao excluir nota:', error);
        showToast('Erro ao excluir nota', 'error');
    } finally {
        hideLoading();
    }
}

// Fornecedores
async function buscarFornecedores(page = 1) {
    console.log('Buscando fornecedores...');
    showLoading();
    try {
        const search = getElementValue('search-fornecedores') || '';
        
        const params = new URLSearchParams({
            page: page,
            per_page: 20,
            search: search
        });
        
        const response = await fetch(`${API_BASE}/fornecedores?${params}`);
        const data = await response.json();
        
        if (data.success) {
            console.log('Fornecedores carregados:', data.data.length);
            renderFornecedores(data.data);
            if (data.pagination) {
                renderPagination('pagination-fornecedores', data.pagination, buscarFornecedores);
            }
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
    if (!tbody) return;
    
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
            <td>${fornecedor.cidade}/${fornecedor.uf}</td>
            <td>${fornecedor.telefone || '-'}</td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn edit" onclick="editarFornecedor(${fornecedor.id})" title="Editar">
                        ✏️
                    </button>
                    <button class="action-btn delete" onclick="excluirFornecedor(${fornecedor.id})" title="Excluir">
                        🗑️
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function editarFornecedor(id) {
    try {
        const response = await fetch(`${API_BASE}/fornecedores/${id}`);
        const data = await response.json();
        
        if (data.success) {
            const fornecedor = data.data;
            
            // Preencher formulário
            setElementValue('fornecedor-cnpj', fornecedor.cnpj);
            setElementValue('fornecedor-razao-social', fornecedor.razao_social);
            setElementValue('fornecedor-nome-fantasia', fornecedor.nome_fantasia);
            setElementValue('fornecedor-endereco', fornecedor.endereco);
            setElementValue('fornecedor-cidade', fornecedor.cidade);
            setElementValue('fornecedor-uf', fornecedor.uf);
            setElementValue('fornecedor-cep', fornecedor.cep);
            setElementValue('fornecedor-telefone', fornecedor.telefone);
            setElementValue('fornecedor-email', fornecedor.email);
            
            // Definir ID para edição
            document.getElementById('form-fornecedor').dataset.editId = id;
            
            abrirModal('modal-fornecedor');
        }
    } catch (error) {
        console.error('Erro ao carregar fornecedor:', error);
        showToast('Erro ao carregar dados do fornecedor', 'error');
    }
}

async function excluirFornecedor(id) {
    if (!confirm('Tem certeza que deseja excluir este fornecedor?')) return;
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/fornecedores/${id}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Fornecedor excluído com sucesso!', 'success');
            buscarFornecedores();
            carregarFornecedores(); // Recarregar dropdowns
        } else {
            showToast(result.error || 'Erro ao excluir fornecedor', 'error');
        }
    } catch (error) {
        console.error('Erro ao excluir fornecedor:', error);
        showToast('Erro ao excluir fornecedor', 'error');
    } finally {
        hideLoading();
    }
}

// Tipos de Despesa
async function buscarTiposDespesa(page = 1) {
    console.log('Buscando tipos de despesa...');
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/tipos-despesa`);
        const data = await response.json();
        
        if (data.success) {
            console.log('Tipos de despesa carregados:', data.data.length);
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
    if (!tbody) return;
    
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
            <td><span class="status-badge ${tipo.ativo ? 'status-ativo' : 'status-inativo'}">${tipo.ativo ? 'Ativo' : 'Inativo'}</span></td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn edit" onclick="editarTipoDespesa(${tipo.id})" title="Editar">
                        ✏️
                    </button>
                    <button class="action-btn delete" onclick="excluirTipoDespesa(${tipo.id})" title="Excluir">
                        🗑️
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function editarTipoDespesa(id) {
    try {
        const response = await fetch(`${API_BASE}/tipos-despesa/${id}`);
        const data = await response.json();
        
        if (data.success) {
            const tipo = data.data;
            
            // Preencher formulário
            setElementValue('tipo-nome', tipo.nome);
            setElementValue('tipo-descricao', tipo.descricao);
            setElementValue('tipo-ativo', tipo.ativo);
            
            // Definir ID para edição
            document.getElementById('form-tipo-despesa').dataset.editId = id;
            
            abrirModal('modal-tipo-despesa');
        }
    } catch (error) {
        console.error('Erro ao carregar tipo de despesa:', error);
        showToast('Erro ao carregar dados do tipo de despesa', 'error');
    }
}

async function excluirTipoDespesa(id) {
    if (!confirm('Tem certeza que deseja excluir este tipo de despesa?')) return;
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/tipos-despesa/${id}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Tipo de despesa excluído com sucesso!', 'success');
            buscarTiposDespesa();
            carregarTiposDespesa(); // Recarregar dropdowns
        } else {
            showToast(result.error || 'Erro ao excluir tipo de despesa', 'error');
        }
    } catch (error) {
        console.error('Erro ao excluir tipo de despesa:', error);
        showToast('Erro ao excluir tipo de despesa', 'error');
    } finally {
        hideLoading();
    }
}

// Comprovantes
async function buscarComprovantes() {
    console.log('Buscando comprovantes...');
    const tbody = document.getElementById('lista-comprovantes');
    if (tbody) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">Funcionalidade em desenvolvimento</td></tr>';
    }
}

// Extratos Bancários
async function buscarExtratosBancarios() {
    console.log('Buscando extratos bancários...');
    const tbody = document.getElementById('lista-extratos');
    if (tbody) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">Funcionalidade em desenvolvimento</td></tr>';
    }
}

// Handlers de Formulários
async function handleUploadXML(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/notas-fiscais/upload`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message || 'XML processado com sucesso!', 'success');
            fecharModal('modal-upload-xml');
            e.target.reset();
            buscarNotasFiscais();
            atualizarDashboard();
        } else {
            showToast(result.error || 'Erro ao processar XML', 'error');
        }
    } catch (error) {
        console.error('Erro ao fazer upload do XML:', error);
        showToast('Erro ao processar XML', 'error');
    } finally {
        hideLoading();
    }
}

async function handleSalvarContaPagar(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    const editId = e.target.dataset.editId;
    
    showLoading();
    try {
        const url = editId ? `${API_BASE}/contas-pagar/${editId}` : `${API_BASE}/contas-pagar`;
        const method = editId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message || 'Conta salva com sucesso!', 'success');
            fecharModal('modal-conta-pagar');
            e.target.reset();
            delete e.target.dataset.editId;
            buscarContasPagar();
            atualizarDashboard();
        } else {
            showToast(result.error || 'Erro ao salvar conta', 'error');
        }
    } catch (error) {
        console.error('Erro ao salvar conta:', error);
        showToast('Erro ao salvar conta', 'error');
    } finally {
        hideLoading();
    }
}

async function handleSalvarFornecedor(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    const editId = e.target.dataset.editId;
    
    showLoading();
    try {
        const url = editId ? `${API_BASE}/fornecedores/${editId}` : `${API_BASE}/fornecedores`;
        const method = editId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message || 'Fornecedor salvo com sucesso!', 'success');
            fecharModal('modal-fornecedor');
            e.target.reset();
            delete e.target.dataset.editId;
            buscarFornecedores();
            carregarFornecedores(); // Recarregar dropdowns
        } else {
            showToast(result.error || 'Erro ao salvar fornecedor', 'error');
        }
    } catch (error) {
        console.error('Erro ao salvar fornecedor:', error);
        showToast('Erro ao salvar fornecedor', 'error');
    } finally {
        hideLoading();
    }
}

async function handleSalvarTipoDespesa(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    const editId = e.target.dataset.editId;
    
    showLoading();
    try {
        const url = editId ? `${API_BASE}/tipos-despesa/${editId}` : `${API_BASE}/tipos-despesa`;
        const method = editId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message || 'Tipo de despesa salvo com sucesso!', 'success');
            fecharModal('modal-tipo-despesa');
            e.target.reset();
            delete e.target.dataset.editId;
            buscarTiposDespesa();
            carregarTiposDespesa(); // Recarregar dropdowns
        } else {
            showToast(result.error || 'Erro ao salvar tipo de despesa', 'error');
        }
    } catch (error) {
        console.error('Erro ao salvar tipo de despesa:', error);
        showToast('Erro ao salvar tipo de despesa', 'error');
    } finally {
        hideLoading();
    }
}

// Funções de Utilidade
function getElementValue(id) {
    const element = document.getElementById(id);
    return element ? element.value : '';
}

function setElementValue(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.value = value || '';
    }
}

function updateElement(id, content) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = content;
    }
}

function showLoading() {
    // Implementar loading se necessário
    console.log('Loading...');
}

function hideLoading() {
    // Implementar hide loading se necessário
    console.log('Loading finished');
}

function showToast(message, type = 'info') {
    console.log(`Toast ${type}:`, message);
    alert(message); // Implementação simples
}

function abrirModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        modal.classList.add('show');
    }
}

function fecharModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('show');
    }
}

function showModal(title, content) {
    alert(`${title}\n\n${content}`); // Implementação simples
}

function formatCurrency(value) {
    if (!value) return 'R$ 0,00';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

function renderPagination(containerId, pagination, callback) {
    // Implementação simples de paginação
    const container = document.getElementById(containerId);
    if (container && pagination.pages > 1) {
        let html = '';
        for (let i = 1; i <= pagination.pages; i++) {
            html += `<button onclick="${callback.name}(${i})" ${i === pagination.page ? 'class="active"' : ''}>${i}</button>`;
        }
        container.innerHTML = html;
    }
}

function aplicarFiltros() {
    if (currentSection === 'contas-pagar') {
        buscarContasPagar();
    } else if (currentSection === 'notas-fiscais') {
        buscarNotasFiscais();
    } else if (currentSection === 'fornecedores') {
        buscarFornecedores();
    }
}

// Expor funções globalmente para onclick
window.pagarConta = pagarConta;
window.editarContaPagar = editarContaPagar;
window.excluirContaPagar = excluirContaPagar;
window.visualizarNota = visualizarNota;
window.excluirNota = excluirNota;
window.editarFornecedor = editarFornecedor;
window.excluirFornecedor = excluirFornecedor;
window.editarTipoDespesa = editarTipoDespesa;
window.excluirTipoDespesa = excluirTipoDespesa;
window.buscarContasPagar = buscarContasPagar;
window.buscarNotasFiscais = buscarNotasFiscais;
window.buscarFornecedores = buscarFornecedores;
window.aplicarFiltros = aplicarFiltros;

console.log('Script carregado com sucesso!');

