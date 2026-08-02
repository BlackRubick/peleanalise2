interface Notification {
  id:      string;
  type:    "success" | "error" | "warning" | "info";
  title:   string;
  message?: string;
}

const notifications = ref<Notification[]>([]);

export function useNotification() {
  function add(n: Omit<Notification, "id">) {
    const id = Math.random().toString(36).slice(2);
    notifications.value.push({ id, ...n });
    setTimeout(() => remove(id), 4500);
  }

  function remove(id: string) {
    notifications.value = notifications.value.filter((n) => n.id !== id);
  }

  const success = (title: string, message?: string) => add({ type: "success", title, message });
  const error   = (title: string, message?: string) => add({ type: "error",   title, message });
  const warning = (title: string, message?: string) => add({ type: "warning", title, message });
  const info    = (title: string, message?: string) => add({ type: "info",    title, message });

  return { notifications: readonly(notifications), success, error, warning, info, remove };
}
