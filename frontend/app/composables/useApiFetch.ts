import { useAuthStore } from "~/stores/auth";

type ApiFetchOpts = Omit<RequestInit, "body"> & {
  body?: unknown;
  query?: Record<string, unknown>;
};

export async function useApiFetch<T>(
  url: string,
  opts: ApiFetchOpts = {}
): Promise<T> {
  const auth   = useAuthStore();
  const config = useRuntimeConfig();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(opts.headers as Record<string, string>),
  };

  if (auth.accessToken) {
    headers["Authorization"] = `Bearer ${auth.accessToken}`;
  }

  let endpoint = url;
  if (opts.query && Object.keys(opts.query).length > 0) {
    const params = new URLSearchParams(
      Object.entries(opts.query)
        .filter(([, v]) => v !== undefined && v !== null)
        .map(([k, v]) => [k, String(v)])
    );
    endpoint = `${url}?${params}`;
  }

  try {
    return await $fetch<T>(endpoint, {
      ...opts,
      headers,
    });
  } catch (err: unknown) {
    const e = err as { status?: number; statusCode?: number };
    if ((e?.status ?? e?.statusCode) === 401 && auth.refreshToken) {
      await auth.refresh();
      headers["Authorization"] = `Bearer ${auth.accessToken}`;
      return await $fetch<T>(endpoint, { ...opts, headers });
    }
    throw err;
  }
}
