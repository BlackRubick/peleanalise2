import { defineStore } from "pinia";

export interface Patient {
  id:          string;
  firstName:   string;
  lastName:    string;
  sex:         string;
  birthDate:   string;
  curp?:       string;
  phone?:      string;
  email?:      string;
  address?:    string;
  observations?: string;
  createdAt:   string;
  _count?:     { studies: number };
}

interface PatientsState {
  list:    Patient[];
  current: Patient | null;
  loading: boolean;
  meta: {
    total: number;
    page:  number;
    limit: number;
    pages: number;
  };
}

export const usePatientsStore = defineStore("patients", {
  state: (): PatientsState => ({
    list:    [],
    current: null,
    loading: false,
    meta:    { total: 0, page: 1, limit: 15, pages: 0 },
  }),

  actions: {
    async fetchAll(params: Record<string, unknown> = {}) {
      this.loading = true;
      try {
        const res = await useApiFetch<{ data: Patient[]; meta: typeof this.meta }>(
          "/api/patients",
          { query: params }
        );
        this.list = res.data;
        this.meta = res.meta;
      } finally {
        this.loading = false;
      }
    },

    async fetchOne(id: string) {
      this.loading = true;
      try {
        this.current = await useApiFetch<Patient>(`/api/patients/${id}`);
      } finally {
        this.loading = false;
      }
    },

    async create(data: Omit<Patient, "id" | "createdAt" | "_count">) {
      const patient = await useApiFetch<Patient>("/api/patients", {
        method: "POST",
        body:   data,
      });
      this.list.unshift(patient);
      return patient;
    },

    async update(id: string, data: Partial<Patient>) {
      const patient = await useApiFetch<Patient>(`/api/patients/${id}`, {
        method: "PUT",
        body:   data,
      });
      const idx = this.list.findIndex((p) => p.id === id);
      if (idx !== -1) this.list[idx] = patient;
      if (this.current?.id === id) this.current = patient;
      return patient;
    },

    async remove(id: string) {
      await useApiFetch(`/api/patients/${id}`, { method: "DELETE" });
      this.list = this.list.filter((p) => p.id !== id);
    },
  },
});
