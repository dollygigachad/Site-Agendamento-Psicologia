const API_BASE_URL = 'http://localhost:8000';
const API_TIMEOUT = 10000; // 10 segundos

const app = {
  currentTab: 'appointments',
  appointments: [],
  patients: [],
  rooms: [],
  users: [],

  init() {
    console.log('🔧 Inicializando aplicação...', API_BASE_URL);
    this.setupEventListeners();
    this.loadAllData();
    // Recarregar dados a cada 10 segundos
    setInterval(() => this.loadAllData(), 10000);
  },

  setupEventListeners() {
    // Tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => this.switchTab(btn.dataset.tab));
    });

    // Forms
    document.getElementById('appointmentForm')?.addEventListener('submit', (e) => this.handleAppointmentForm(e));
    document.getElementById('patientForm')?.addEventListener('submit', (e) => this.handlePatientForm(e));
    document.getElementById('roomForm')?.addEventListener('submit', (e) => this.handleRoomForm(e));
    document.getElementById('userForm')?.addEventListener('submit', (e) => this.handleUserForm(e));

    // Busca/Filtro
    document.getElementById('appointmentSearch')?.addEventListener('input', (e) => this.filterAppointments(e.target.value));
    document.getElementById('patientSearch')?.addEventListener('input', (e) => this.filterPatients(e.target.value));
    document.getElementById('roomSearch')?.addEventListener('input', (e) => this.filterRooms(e.target.value));
    document.getElementById('userSearch')?.addEventListener('input', (e) => this.filterUsers(e.target.value));
  },

  async loadAllData() {
    try {
      console.log('📥 Carregando dados da API...');
      
      const appointmentsPromise = this.fetchData('appointments').then(data => {
        this.appointments = data;
        this.renderAppointmentsTable();
        console.log(`✓ ${this.appointments.length} agendamentos carregados`);
      });

      const patientsPromise = this.fetchData('patients').then(data => {
        this.patients = data;
        this.renderPatientsTable();
        console.log(`✓ ${this.patients.length} pacientes carregados`);
      });

      const roomsPromise = this.fetchData('rooms').then(data => {
        this.rooms = data;
        this.renderRoomsTable();
        console.log(`✓ ${this.rooms.length} salas carregadas`);
      });

      const usersPromise = this.fetchData('users').then(data => {
        this.users = data;
        this.renderUsersTable();
        console.log(`✓ ${this.users.length} usuários carregados`);
      });

      await Promise.all([appointmentsPromise, patientsPromise, roomsPromise, usersPromise]);
      
      this.populateSelects();
      console.log('✓ Todos os dados carregados com sucesso');
    } catch (error) {
      console.error('❌ Erro ao carregar dados:', error);
      this.showAlert('Erro ao conectar com a API: ' + error.message, 'danger');
    }
  },

  async fetchData(endpoint) {
    try {
      console.log(`  Buscando ${endpoint}...`);
      
      // Criar timeout com AbortController
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);
      
      const response = await fetch(`${API_BASE_URL}/api/${endpoint}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        console.error(`  ✗ Erro HTTP ${response.status} para ${endpoint}`);
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      const result = Array.isArray(data) ? data : data.items || data || [];
      console.log(`  ✓ ${endpoint} carregado (${result.length} items)`);
      return result;
    } catch (error) {
      if (error.name === 'AbortError') {
        console.error(`  ✗ Timeout ao buscar ${endpoint} (${API_TIMEOUT}ms)`);
      } else {
        console.error(`  ✗ Erro ao buscar ${endpoint}:`, error.message);
      }
      return [];
    }
  },

  switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.add('hidden'));
    document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');
    document.querySelector(`#${tabName}-tab`)?.classList.remove('hidden');
    this.currentTab = tabName;
  },

  renderAppointmentsTable() {
    const tbody = document.querySelector('#appointmentsTable tbody');
    if (!tbody) return;

    if (this.appointments.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Nenhum agendamento encontrado</td></tr>';
      return;
    }

    tbody.innerHTML = this.appointments.map(apt => {
      const patientName = apt.patient_name || (apt.patient && apt.patient.name) || '-';
      const roomName = apt.room_name || (apt.room && apt.room.name) || '-';
      let startDate = '-';
      let startTime = '-';
      let endTime = '-';
      if (apt.start_dt) {
        const d = new Date(apt.start_dt);
        if (!isNaN(d)) {
          startDate = d.toLocaleDateString('pt-BR');
          startTime = d.toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'});
        }
      }
      if (apt.end_dt) {
        const d = new Date(apt.end_dt);
        if (!isNaN(d)) {
          endTime = d.toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'});
        }
      }
      const status = apt.status || 'scheduled';
      return `<tr>
        <td>${apt.id || '-'}</td>
        <td>${patientName}</td>
        <td>${roomName}</td>
        <td>${startDate}</td>
        <td>${startTime} - ${endTime}</td>
        <td><span class="badge ${this.getStatusBadge(status)}">${this.getStatusLabel(status)}</span></td>
        <td>
          <button class="btn btn-sm btn-danger" onclick="app.deleteItem('appointments', ${apt.id})">🗑️</button>
        </td>
      </tr>`;
    }).join('');
  },

  renderPatientsTable() {
    const tbody = document.querySelector('#patientsTable tbody');
    if (!tbody) return;

    if (this.patients.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Nenhum paciente encontrado</td></tr>';
      return;
    }

    tbody.innerHTML = this.patients.map(patient => {
      let birthdate = '-';
      if (patient.birthdate) {
        const d = new Date(patient.birthdate);
        if (!isNaN(d)) {
          birthdate = d.toLocaleDateString('pt-BR');
        }
      }
      const notes = patient.notes || '-';
      return `<tr>
        <td>${patient.id || '-'}</td>
        <td>${patient.name || '-'}</td>
        <td>${patient.email || '-'}</td>
        <td>${patient.phone || '-'}</td>
        <td>${birthdate}</td>
        <td>${notes}</td>
        <td>
          <button class="btn btn-sm btn-danger" onclick="app.deleteItem('patients', ${patient.id})">🗑️</button>
        </td>
      </tr>`;
    }).join('');
  },

  renderRoomsTable() {
    const tbody = document.querySelector('#roomsTable tbody');
    if (!tbody) return;

    if (this.rooms.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Nenhuma sala encontrada</td></tr>';
      return;
    }

    tbody.innerHTML = this.rooms.map(room => {
      return `<tr>
        <td>${room.id || '-'}</td>
        <td>${room.name || '-'}</td>
        <td>${room.description || '-'}</td>
        <td>${room.capacity || '-'}</td>
        <td>
          <button class="btn btn-sm btn-danger" onclick="app.deleteItem('rooms', ${room.id})">🗑️</button>
        </td>
      </tr>`;
    }).join('');
  },

  renderUsersTable() {
    const tbody = document.querySelector('#usersTable tbody');
    if (!tbody) return;

    if (this.users.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Nenhum usuário encontrado</td></tr>';
      return;
    }

    tbody.innerHTML = this.users.map(user => {
        const roleLabel = this.getRoleLabel(user.role) || '-';
      return `<tr>
        <td>${user.id || '-'}</td>
        <td>${user.name || '-'}</td>
        <td>${user.email || '-'}</td>
          <td><span class="badge badge-info">${this.getRoleLabel(user.role) || '-'}</span></td>
        <td>
          <button class="btn btn-sm btn-danger" onclick="app.deleteItem('users', ${user.id})">🗑️</button>
        </td>
      </tr>`;
    }).join('');
  },

  filterAppointments(query) {
    const tbody = document.querySelector('#appointmentsTable tbody');
    if (!tbody) return;
    const q = (query || '').toLowerCase();
    const filtered = this.appointments.filter(apt => {
      const patient = (apt.patient_name || apt.patient?.name || '').toLowerCase();
      const room = (apt.room_name || apt.room?.name || '').toLowerCase();
      const status = (this.getStatusLabel(apt.status || 'scheduled') || '').toLowerCase();
      const date = apt.start_dt ? new Date(apt.start_dt).toLocaleDateString('pt-BR').toLowerCase() : '';
      return patient.includes(q) || room.includes(q) || status.includes(q) || date.includes(q);
    });
    if (filtered.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Nenhum resultado</td></tr>';
      return;
    }
    tbody.innerHTML = filtered.map(apt => `
      <tr>
        <td>${apt.id || '-'}</td>
        <td>${apt.patient_name || apt.patient?.name || '-'}</td>
        <td>${apt.room_name || apt.room?.name || '-'}</td>
        <td>${apt.start_dt ? new Date(apt.start_dt).toLocaleDateString('pt-BR') : '-'}</td>
        <td>${apt.start_dt ? new Date(apt.start_dt).toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'}) : '-'} - ${apt.end_dt ? new Date(apt.end_dt).toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'}) : '-'}</td>
        <td><span class="badge ${this.getStatusBadge(apt.status)}">${this.getStatusLabel(apt.status || 'scheduled')}</span></td>
        <td>
          <button class="btn btn-sm btn-danger" onclick="app.deleteItem('appointments', ${apt.id})">🗑️</button>
        </td>
      </tr>
    `).join('');
  },

  filterPatients(query) {
    const tbody = document.querySelector('#patientsTable tbody');
    if (!tbody) return;
    const q = (query || '').toLowerCase();
    const filtered = this.patients.filter(patient => {
      const name = (patient.name || '').toLowerCase();
      const email = (patient.email || '').toLowerCase();
      const phone = (patient.phone || '').toLowerCase();
      const birthdate = patient.birthdate ? new Date(patient.birthdate).toLocaleDateString('pt-BR').toLowerCase() : '';
      const isChild = patient.is_child ? 'sim' : 'não';
      return name.includes(q) || email.includes(q) || phone.includes(q) || birthdate.includes(q) || isChild.includes(q);
    });
    if (filtered.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Nenhum resultado</td></tr>';
      return;
    }
    tbody.innerHTML = filtered.map(patient => {
      let birthdate = '-';
      if (patient.birthdate) {
        const d = new Date(patient.birthdate);
        if (!isNaN(d)) {
          birthdate = d.toLocaleDateString('pt-BR');
        }
      }
      return `<tr>
        <td>${patient.id || '-'}</td>
        <td>${patient.name || '-'}</td>
        <td>${patient.email || '-'}</td>
        <td>${patient.phone || '-'}</td>
        <td>${birthdate}</td>
        <td>
          <button class="btn btn-sm btn-danger" onclick="app.deleteItem('patients', ${patient.id})">🗑️</button>
        </td>
      </tr>`;
    }).join('');
  },

  filterRooms(query) {
    const tbody = document.querySelector('#roomsTable tbody');
    if (!tbody) return;
    const q = (query || '').toLowerCase();
    const filtered = this.rooms.filter(room => {
      const name = (room.name || '').toLowerCase();
      const desc = (room.description || '').toLowerCase();
      const capacity = (room.capacity ? String(room.capacity) : '').toLowerCase();
      return name.includes(q) || desc.includes(q) || capacity.includes(q);
    });
    if (filtered.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Nenhum resultado</td></tr>';
      return;
    }
    tbody.innerHTML = filtered.map(room => `
      <tr>
        <td>${room.id || '-'}</td>
        <td>${room.name || '-'}</td>
        <td>${room.description || '-'}</td>
        <td>${room.capacity || '-'}</td>
        <td>
          <button class="btn btn-sm btn-danger" onclick="app.deleteItem('rooms', ${room.id})">🗑️</button>
        </td>
      </tr>
    `).join('');
  },

  filterUsers(query) {
    const tbody = document.querySelector('#usersTable tbody');
    if (!tbody) return;
    const q = (query || '').toLowerCase();
    const filtered = this.users.filter(user => {
      const name = (user.name || '').toLowerCase();
      const email = (user.email || '').toLowerCase();
      const role = (this.getRoleLabel(user.role) || '').toLowerCase();
      return name.includes(q) || email.includes(q) || role.includes(q);
    });
    if (filtered.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Nenhum resultado</td></tr>';
      return;
    }
    tbody.innerHTML = filtered.map(user => `
      <tr>
        <td>${user.id || '-'}</td>
        <td>${user.name || '-'}</td>
        <td>${user.email || '-'}</td>
        <td><span class="badge badge-info">${this.getRoleLabel(user.role) || '-'}</span></td>
        <td>
          <button class="btn btn-sm btn-danger" onclick="app.deleteItem('users', ${user.id})">🗑️</button>
        </td>
      </tr>
    `).join('');
  },

  async deleteItem(endpoint, id) {
    if (!confirm(`Tem certeza que deseja deletar este item?`)) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/${endpoint}/${id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
      });
      if (response.ok) {
        this.showAlert('Item deletado com sucesso!', 'success');
        this.loadAllData();
      } else {
        try {
          const errorData = await response.json();
          this.showAlert(`Erro ao deletar: ${errorData.detail || 'Erro desconhecido'}`, 'danger');
        } catch {
          this.showAlert(`Erro ao deletar item (${response.status})`, 'danger');
        }
      }
    } catch (error) {
      console.error('Erro:', error);
      this.showAlert('Erro ao deletar item', 'danger');
    }
  },

  async handleAppointmentForm(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const entries = Object.fromEntries(formData);
    const appointmentDate = entries.appointment_date;
    const startTime = entries.start_time;
    const endTime = entries.end_time;
    if (!appointmentDate || !startTime || !endTime) {
      this.showAlert('Data e horário são obrigatórios', 'danger');
      return;
    }
    const room_id = parseInt(entries.room_id, 10);
    const patient_id = parseInt(entries.patient_id, 10);
    const student_id = parseInt(entries.student_id, 10);
    const supervisor_id = parseInt(entries.supervisor_id, 10);
    if (!room_id || !patient_id || !student_id || !supervisor_id) {
      this.showAlert('Sala, paciente, estagiário e supervisor são obrigatórios', 'danger');
      return;
    }
    const start_dt = new Date(`${appointmentDate}T${startTime}`);
    const end_dt = new Date(`${appointmentDate}T${endTime}`);
    const now = new Date();
    if (start_dt <= now) {
      this.showAlert('A data/hora do agendamento deve ser no futuro', 'danger');
      return;
    }
    if (end_dt <= start_dt) {
      this.showAlert('A hora de fim deve ser posterior à hora de início', 'danger');
      return;
    }
    const payload = {
      start_dt: start_dt.toISOString(),
      end_dt: end_dt.toISOString(),
      room_id: Number(room_id),
      patient_id: Number(patient_id),
      student_id: Number(student_id),
      supervisor_id: Number(supervisor_id),
      notes: entries.notes || null,
    };
    try {
      const response = await fetch(`${API_BASE_URL}/api/appointments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const respText = await response.text();
      let respJson = null;
      try { respJson = JSON.parse(respText); } catch {}
      if (response.ok) {
        this.showAlert('Agendamento criado com sucesso!', 'success');
        e.target.reset();
        this.loadAllData();
      } else {
        let msg = 'Erro ao criar agendamento';
        // FastAPI custom handler returns `message`, enquanto o padrão usa `detail`.
        const serverMsg = respJson && (respJson.detail || respJson.message);
        if (serverMsg) msg += ': ' + serverMsg;
        else msg += ': ' + respText;
        this.showAlert(msg, 'danger');
      }
    } catch (error) {
      console.error('Erro:', error);
      this.showAlert('Erro ao criar agendamento', 'danger');
    }
  },

  async handlePatientForm(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);


    // Converter is_child para booleano
    if (data.is_child !== undefined) {
      data.is_child = data.is_child === 'true' || data.is_child === true;
    }

    // Converter birthdate vazio para null
    if (!data.birthdate) {
      data.birthdate = null;
    }

    // Garantir que notes seja string ou null
    if (typeof data.notes === 'undefined' || data.notes === '') {
      data.notes = null;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/patients`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (response.ok) {
        this.showAlert('Paciente criado com sucesso!', 'success');
        e.target.reset();
        this.loadAllData();
      } else {
        const errorText = await response.text();
        console.error('Erro ao criar paciente:', response.status, errorText);
        this.showAlert('Erro ao criar paciente: ' + response.status, 'danger');
      }
    } catch (error) {
      console.error('Erro:', error);
      this.showAlert('Erro ao criar paciente', 'danger');
    }
  },

  async handleRoomForm(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    
    // Converter capacity para inteiro
    if (data.capacity) {
      data.capacity = parseInt(data.capacity, 10);
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/rooms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (response.ok) {
        this.showAlert('Sala criada com sucesso!', 'success');
        e.target.reset();
        this.loadAllData();
      } else {
        this.showAlert('Erro ao criar sala', 'danger');
      }
    } catch (error) {
      console.error('Erro:', error);
      this.showAlert('Erro ao criar sala', 'danger');
    }
  },

  async handleUserForm(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    // Corrigir role para o formato esperado pelo backend (enum)
    if (data.role) {
      // Enviar role no formato que o backend espera (minúsculo)
      const roleMap = { 'admin': 'admin', 'professor': 'professor', 'student': 'student' };
      data.role = roleMap[data.role.toLowerCase()] || 'student';
    } else {
      data.role = 'student';
    }
    if (!data.name || !data.email || !data.password) {
      this.showAlert('Nome, email e senha são obrigatórios', 'danger');
      return;
    }
    if (data.password.length < 8) {
      this.showAlert('A senha deve ter pelo menos 8 caracteres', 'danger');
      return;
    }
    const payload = {
      name: data.name,
      email: data.email,
      password: data.password,
      role: data.role
    };
    try {
      const response = await fetch(`${API_BASE_URL}/api/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const respText = await response.text();
      let respJson = null;
      try { respJson = JSON.parse(respText); } catch {}
      if (response.ok) {
        this.showAlert('Usuário criado com sucesso!', 'success');
        e.target.reset();
        this.loadAllData();
      } else {
        // Log completo para diagnóstico
        console.error('Erro ao criar usuário', response.status, respJson || respText);

        // Formatar message quando o backend retorna detalhes de validação (422)
        let msg = 'Erro ao criar usuário';
        if (respJson) {
          // FastAPI ValidationError: { detail: [ { loc, msg, type }, ... ] }
          if (Array.isArray(respJson.detail)) {
            const details = respJson.detail.map(d => d.msg || JSON.stringify(d)).join('; ');
            msg += ': ' + details;
          } else if (respJson.detail && typeof respJson.detail === 'string') {
            msg += ': ' + respJson.detail;
          } else if (respJson.message) {
            msg += ': ' + respJson.message;
          } else {
            msg += ': ' + JSON.stringify(respJson);
          }
        } else {
          msg += ': ' + respText;
        }
        this.showAlert(msg, 'danger');
      }
    } catch (error) {
      console.error('Erro:', error);
      this.showAlert('Erro ao criar usuário', 'danger');
    }
  },

  populateSelects() {
    // Preencher select de pacientes
    const patientSelect = document.querySelector('select[name="patient_id"]');
    if (patientSelect) {
      const prev = patientSelect.value;
      // If user is interacting with this select, don't overwrite it
      if (document.activeElement !== patientSelect) {
        patientSelect.innerHTML = '<option value="">Selecione um paciente...</option>' +
          this.patients.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
        if (prev) {
          const found = Array.from(patientSelect.options).some(o => o.value === prev);
          if (found) patientSelect.value = prev;
        }
      }
    }

    // Preencher select de salas
    const roomSelect = document.querySelector('select[name="room_id"]');
    if (roomSelect) {
      const prev = roomSelect.value;
      if (document.activeElement !== roomSelect) {
        roomSelect.innerHTML = '<option value="">Selecione uma sala...</option>' +
          this.rooms.map(r => `<option value="${r.id}">${r.name}</option>`).join('');
        if (prev) {
          const found = Array.from(roomSelect.options).some(o => o.value === prev);
          if (found) roomSelect.value = prev;
        }
      }
    }

    // Preencher select de estagiários (usuários com role student)
    const studentSelect = document.querySelector('select[name="student_id"]');
    if (studentSelect) {
      const prev = studentSelect.value;
      if (document.activeElement !== studentSelect) {
        const students = this.users.filter(u => {
          const role = (u.role || '').toString().toLowerCase();
          return role === 'student';
        });
        studentSelect.innerHTML = '<option value="">Selecione um estagiário...</option>' +
          students.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
        if (prev) {
          const found = Array.from(studentSelect.options).some(o => o.value === prev);
          if (found) studentSelect.value = prev;
        }
      }
    }

    // Preencher select de supervisores (usuários com role professor/admin)
    const supervisorSelect = document.querySelector('select[name="supervisor_id"]');
    if (supervisorSelect) {
      const prev = supervisorSelect.value;
      if (document.activeElement !== supervisorSelect) {
        const professors = this.users.filter(u => {
          const role = (u.role || '').toString().toLowerCase();
          return role === 'professor' || role === 'admin';
        });
        supervisorSelect.innerHTML = '<option value="">Selecione um profissional...</option>' +
          professors.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
        if (prev) {
          const found = Array.from(supervisorSelect.options).some(o => o.value === prev);
          if (found) supervisorSelect.value = prev;
        }
      }
    }
  },

  getStatusBadge(status) {
    const badges = {
      'confirmed': 'badge-success',
      'pending': 'badge-warning',
      'cancelled': 'badge-danger',
      'completed': 'badge-info',
      'scheduled': 'badge-info',
    };
    return badges[status] || 'badge-secondary';
  },

  getStatusLabel(status) {
    const labels = {
      'scheduled': 'Agendado',
      'confirmed': 'Confirmado',
      'pending': 'Pendente',
      'cancelled': 'Cancelado',
      'completed': 'Concluído',
      'in_progress': 'Em andamento',
      'no_show': 'Falta',
    };
    return labels[status] || (typeof status === 'string' ? status : '—');
  },

  getRoleLabel(role) {
    if (!role) return '-';
    const key = role.toString().toLowerCase();
    const map = {
      'admin': 'Administrador',
      'professor': 'Professor',
      'student': 'Estudante',
    };
    return map[key] || role;
  },

  formatError(err) {
    // Formata objetos de erro do backend para mensagem legível
    if (!err) return '';
    if (typeof err === 'string') return err;
    try {
      // FastAPI validation errors: { detail: [ { loc, msg, type }, ... ] }
      if (Array.isArray(err.detail)) {
        return err.detail.map(d => d.msg || JSON.stringify(d)).join('; ');
      }
      if (err.detail && typeof err.detail === 'string') return err.detail;
      if (err.message) return err.message;
      if (err.errors && Array.isArray(err.errors)) {
        return err.errors.map(e => `${e.field}: ${e.message}`).join('; ');
      }
      return JSON.stringify(err);
    } catch (e) {
      return String(err);
    }
  },

  showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;

    const msgSpan = document.createElement('span');
    msgSpan.textContent = typeof message === 'string' ? message : this.formatError(message);

    const closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'alert-close';
    closeBtn.innerText = '×';
    closeBtn.addEventListener('click', () => alertDiv.remove());

    alertDiv.appendChild(msgSpan);
    alertDiv.appendChild(closeBtn);
    alertContainer.appendChild(alertDiv);

    setTimeout(() => alertDiv.remove(), 7000);
  },
};

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  console.log('📄 DOM carregado, inicializando app...');
  app.init();
});
