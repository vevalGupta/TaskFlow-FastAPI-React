import axios from 'axios';

const api = axios.create({ baseURL: '/api/v1', headers: { 'Content-Type': 'application/json' } });

api.interceptors.request.use(cfg => {
  const t = localStorage.getItem('accessToken');
  if (t) cfg.headers.Authorization = `Bearer ${t}`;
  return cfg;
});

let refreshing = false, queue = [];
const flush = (err, token) => { queue.forEach(p => err ? p.reject(err) : p.resolve(token)); queue = []; };

api.interceptors.response.use(r => r, async err => {
  const orig = err.config;
  const code = err.response?.data?.error?.code;
  if (err.response?.status === 401 && code === 'TOKEN_EXPIRED' && !orig._retry) {
    if (refreshing) return new Promise((res, rej) => queue.push({ resolve: res, reject: rej }))
      .then(t => { orig.headers.Authorization = `Bearer ${t}`; return api(orig); });
    orig._retry = true; refreshing = true;
    try {
      const { data } = await axios.post('/api/v1/auth/refresh', { refreshToken: localStorage.getItem('refreshToken') });
      const t = data.data.accessToken;
      localStorage.setItem('accessToken', t);
      localStorage.setItem('refreshToken', data.data.refreshToken);
      flush(null, t); orig.headers.Authorization = `Bearer ${t}`;
      return api(orig);
    } catch (e) { flush(e); localStorage.clear(); window.location.href = '/login'; return Promise.reject(e); }
    finally { refreshing = false; }
  }
  return Promise.reject(err);
});

export const authApi = {
  register: d => api.post('/auth/register', d),
  login:    d => api.post('/auth/login', d),
  logout:   ()=> api.post('/auth/logout'),
  me:       ()=> api.get('/users/me'),
};

export const tasksApi = {
  list:   p  => api.get('/tasks', { params: p }),
  get:    id => api.get(`/tasks/${id}`),
  create: d  => api.post('/tasks', d),
  update: (id,d) => api.patch(`/tasks/${id}`, d),
  remove: id => api.delete(`/tasks/${id}`),
};

export const adminApi = {
  dashboard: () => api.get('/admin/dashboard'),
  tasks:     p  => api.get('/admin/tasks', { params: p }),
  users:     p  => api.get('/users', { params: p }),
  updateRole:(id,role) => api.patch(`/users/${id}/role`, { role }),
  deleteUser: id => api.delete(`/users/${id}`),
};

export const extractError = err => {
  const e = err?.response?.data?.error;
  return { message: e?.message || err?.message || 'Something went wrong', fields: e?.fields || {} };
};

export default api;