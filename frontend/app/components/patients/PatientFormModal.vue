<template>
  <UiModal :model-value="modelValue" :title="patient ? 'Editar paciente' : 'Nuevo paciente'" size="lg" @update:model-value="$emit('update:modelValue', $event)">
    <form @submit.prevent="submit" class="grid grid-cols-2 gap-4">
      <div>
        <label class="label">Nombre(s) *</label>
        <input v-model="form.firstName" class="input" :class="{ 'input-error': errors.firstName }" placeholder="María" />
        <p v-if="errors.firstName" class="field-error">{{ errors.firstName }}</p>
      </div>
      <div>
        <label class="label">Apellidos *</label>
        <input v-model="form.lastName" class="input" :class="{ 'input-error': errors.lastName }" placeholder="González López" />
        <p v-if="errors.lastName" class="field-error">{{ errors.lastName }}</p>
      </div>
      <div>
        <label class="label">Sexo *</label>
        <select v-model="form.sex" class="input" :class="{ 'input-error': errors.sex }">
          <option value="">Seleccionar...</option>
          <option value="MASCULINO">Masculino</option>
          <option value="FEMENINO">Femenino</option>
          <option value="OTRO">Otro</option>
        </select>
        <p v-if="errors.sex" class="field-error">{{ errors.sex }}</p>
      </div>
      <div>
        <label class="label">Fecha de nacimiento *</label>
        <input v-model="form.birthDate" type="date" class="input" :class="{ 'input-error': errors.birthDate }" />
        <p v-if="errors.birthDate" class="field-error">{{ errors.birthDate }}</p>
      </div>
      <div>
        <label class="label">CURP</label>
        <input v-model="form.curp" class="input font-mono text-sm" :class="{ 'input-error': errors.curp }" placeholder="GOML890101HDFNZS03" maxlength="18" />
        <p v-if="errors.curp" class="field-error">{{ errors.curp }}</p>
        <p v-else-if="form.curp" class="mt-1 text-xs" :class="form.curp.length === 18 ? 'text-emerald-500' : 'text-amber-500'">
          {{ form.curp.length }}/18 caracteres
        </p>
      </div>
      <div>
        <label class="label">Teléfono</label>
        <input v-model="form.phone" type="tel" class="input" placeholder="55 1234 5678" />
      </div>
      <div>
        <label class="label">Correo electrónico</label>
        <input v-model="form.email" type="email" class="input" placeholder="paciente@correo.mx" />
      </div>
      <div class="col-span-2">
        <label class="label">Dirección</label>
        <input v-model="form.address" class="input" placeholder="Calle, colonia, ciudad, CP" />
      </div>
      <div class="col-span-2">
        <label class="label">Observaciones</label>
        <textarea v-model="form.observations" class="input h-20 resize-none" placeholder="Antecedentes, alergias, notas..." />
      </div>
    </form>
    <template #footer>
      <button class="btn-secondary" @click="$emit('update:modelValue', false)">Cancelar</button>
      <button class="btn-primary" :disabled="saving" @click="submit">
        {{ saving ? "Guardando..." : (patient ? "Actualizar" : "Crear paciente") }}
      </button>
    </template>
  </UiModal>
</template>

<script setup lang="ts">
import { usePatientsStore, type Patient } from "~/stores/patients";

const props = defineProps<{ modelValue: boolean; patient?: Patient | null }>();
const emit  = defineEmits(["update:modelValue", "saved"]);

const store  = usePatientsStore();
const saving = ref(false);
const errors = reactive<Record<string, string>>({
  firstName: "", lastName: "", sex: "", birthDate: "", curp: "",
});

const form = reactive({
  firstName:    "",
  lastName:     "",
  sex:          "",
  birthDate:    "",
  curp:         "",
  phone:        "",
  email:        "",
  address:      "",
  observations: "",
});

watch(() => props.patient, (p) => {
  if (p) {
    Object.assign(form, {
      firstName:    p.firstName,
      lastName:     p.lastName,
      sex:          p.sex,
      birthDate:    p.birthDate?.slice(0, 10) ?? "",
      curp:         p.curp ?? "",
      phone:        p.phone ?? "",
      email:        p.email ?? "",
      address:      p.address ?? "",
      observations: p.observations ?? "",
    });
  } else {
    Object.keys(form).forEach((k) => ((form as Record<string, string>)[k] = ""));
  }
}, { immediate: true });

function validate() {
  Object.keys(errors).forEach(k => (errors[k] = ""));
  if (!form.firstName) errors.firstName = "El nombre es requerido";
  if (!form.lastName)  errors.lastName  = "Los apellidos son requeridos";
  if (!form.sex)       errors.sex       = "El sexo es requerido";
  if (!form.birthDate) errors.birthDate = "La fecha de nacimiento es requerida";
  if (form.curp && form.curp.length !== 18)
    errors.curp = "El CURP debe tener exactamente 18 caracteres";
  return !Object.values(errors).some(Boolean);
}

async function submit() {
  if (!validate()) return;
  saving.value = true;
  try {
    if (props.patient) {
      await store.update(props.patient.id, form);
    } else {
      await store.create(form as Parameters<typeof store.create>[0]);
    }
    emit("saved");
    emit("update:modelValue", false);
  } catch (err: unknown) {
    const e = err as { data?: { data?: Array<{ path: string[]; message: string }>; message?: string } };
    const zodErrors = e?.data?.data;
    if (Array.isArray(zodErrors)) {
      zodErrors.forEach(({ path, message }) => {
        if (path[0]) errors[path[0]] = message;
      });
    } else {
      errors.firstName = e?.data?.message ?? "Error al guardar";
    }
  } finally {
    saving.value = false;
  }
}
</script>
