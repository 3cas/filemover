// static/api.js

export async function apiCall(endpoint, { method = "GET", params = {}, body = null } = {}) {
    const url = new URL(`http://localhost:8000${endpoint}`);

    if (method === "GET" && params) {
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
    }

    const options = { method, headers: {} };

    if (method === "POST" && body) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
    }

    const res = await fetch(url, options);
    if (!res.ok) {
        const error = await res.text();
        console.error(`API Error (${res.status}):`, error);
        throw new Error(error);
    }
    return await res.json();
}

// Wrapped API calls
export const listFiles = (dirPath) => apiCall("/files", { method: "GET", params: { dir_path: dirPath } });
export const countFiles = (dirPath) => apiCall("/files/count", { method: "GET", params: { dir_path: dirPath } });
export const moveFile = (srcPath, destDir) => apiCall("/files/move", { method: "POST", body: { src_path: srcPath, dest_dir: destDir } });
export const renameFile = (srcPath, newName) => apiCall("/files/rename", { method: "POST", body: { src_path: srcPath, new_name: newName } });
export const previewFile = (filePath) => apiCall("/files/preview", { method: "GET", params: { file_path: filePath } });
export const loadConfig = (path = null) => apiCall("/config", { method: "GET", params: path ? { path } : {} });
export const saveConfig = (config, path = null) => apiCall("/config", { method: "POST", body: { config, path } });
