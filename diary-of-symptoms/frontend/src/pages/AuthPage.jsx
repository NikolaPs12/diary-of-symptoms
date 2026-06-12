export default function AuthPage({
  mode,
  form,
  onChange,
  onSubmit,
  onSwitchMode,
  error,
  copy,
  locale,
  onToggleLocale,
}) {
  const isRegister = mode === "register";

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="surface w-full max-w-xl p-6 md:p-10">
        {/* Header */}
        <div className="mb-10 border-b border-codex-line pb-6">
          <div className="flex items-center justify-between gap-4">
            <div className="text-xs uppercase tracking-[0.28em] text-codex-muted">{copy.appName}</div>
            <button
              type="button"
              onClick={onToggleLocale}
              className="border border-codex-line px-3 py-2 text-xs uppercase tracking-[0.2em] text-codex-black transition hover:bg-codex-black hover:text-codex-white"
            >
              {locale.toUpperCase()}
            </button>
          </div>
          <h1 className="mt-3 text-4xl font-semibold tracking-swiss">
            {isRegister ? copy.auth.registerTitle : copy.auth.loginTitle}
          </h1>
          <p className="mt-3 max-w-md text-sm leading-6 text-codex-muted">
            {isRegister ? copy.auth.registerDescription : copy.auth.loginDescription}
          </p>
        </div>

        {/* Form */}
        <form className="grid gap-4" onSubmit={onSubmit}>
          {isRegister && (
            <>
              <input
                className="field-shell"
                name="name"
                placeholder={copy.auth.fullName}
                value={form.name}
                onChange={onChange}
                required
              />

              <input
                className="field-shell"
                name="age"
                type="number"
                min="0"
                placeholder={copy.auth.age}
                value={form.age}
                onChange={onChange}
              />
            </>
          )}
          
          <input
            className="field-shell"
            name="email"
            type="email"
            placeholder={copy.auth.email}
            value={form.email}
            onChange={onChange}
            required
          />
          
          <input
            className="field-shell"
            name="password"
            type="password"
            placeholder={copy.auth.password}
            value={form.password}
            onChange={onChange}
            required
          />

          {isRegister && (
            <>
              {/* Секция базовых параметров (Вес и Рост) */}
              <div className="grid gap-4 grid-cols-2">
                <input
                  className="field-shell"
                  name="weight"
                  type="number"
                  placeholder={copy.auth.weight}
                  value={form.weight}
                  onChange={onChange}
                />
                <input
                  className="field-shell"
                  name="height"
                  type="number"
                  placeholder={copy.auth.height}
                  value={form.height}
                  onChange={onChange}
                />
              </div>

              {/* Медицинские показатели в две колонки */}
              <div className="grid gap-4 grid-cols-2">
                
                {/* Блок Пульса */}
                <div className="field-shell flex flex-col items-center justify-center py-6 bg-white border border-codex-line">
                  <span className="text-[10px] uppercase tracking-[0.3em] text-codex-muted mb-4">Пульс (bpm)</span>
                  <div className="flex items-center justify-between w-full px-4">
                    <button 
                      type="button" 
                      onClick={() => onChange({ target: { name: 'puls_is_normal', value: (Number(form.puls_is_normal) || 70) - 1 } })}
                      className="text-2xl opacity-20 hover:opacity-100 transition px-2"
                    >
                      −
                    </button>
                    <input
                      type="number"
                      name="puls_is_normal"
                      className="w-[70px] bg-transparent text-center text-3xl font-mono tracking-tighter focus:outline-none"
                      value={form.puls_is_normal}
                      onChange={(e) => {
                        // Оставляем только цифры и берем первые 3 символа
                        const val = e.target.value.replace(/\D/g, "").slice(0, 3);
                        onChange({ target: { name: 'puls_is_normal', value: val } });
                      }}
                      placeholder="70"
                    />
                    <button 
                      type="button" 
                      onClick={() => onChange({ target: { name: 'puls_is_normal', value: (Number(form.puls_is_normal) || 70) + 1 } })}
                      className="text-2xl opacity-20 hover:opacity-100 transition px-2"
                    >
                      +
                    </button>
                  </div>
                </div>

                {/* Блок Давления */}
                <div className="field-shell flex flex-col items-center justify-center py-6 bg-white border border-codex-line">
                  <span className="text-[10px] uppercase tracking-[0.3em] text-codex-muted mb-4">Давление (АД)</span>
                  <div className="flex items-center justify-center font-mono text-3xl tracking-tighter">
                    <input
                      type="number"
                      className="w-[60px] bg-transparent text-right focus:outline-none placeholder:opacity-10"
                      placeholder="120"
                      value={form.pressure_is_normal?.split('/')[0] || ''}
                      onChange={(e) => {
                        // 1. Оставляем только цифры и ограничиваем 3 символами то, что вводит пользователь
                        const newVal = e.target.value.replace(/\D/g, "").slice(0, 3);
                        
                        // 2. Безопасно достаем вторую часть (диастолу)
                        const parts = form.pressure_is_normal?.split('/') || ['', '80'];
                        const dia = parts[1] || '80';

                        // 3. Отправляем в общий onChange
                        onChange({ 
                          target: { 
                            name: 'pressure_is_normal', 
                            value: `${newVal}/${dia}` 
                          } 
                        });
                      }}
                    />
                    <span className="mx-1 opacity-20 font-light">/</span>
                    <input
                      type="number"
                      className="w-[60px] bg-transparent text-left focus:outline-none placeholder:opacity-10"
                      placeholder="80"
                      value={form.pressure_is_normal?.split('/')[1] || ''}
                      onChange={(e) => {
                        const newVal = e.target.value.replace(/\D/g, "").slice(0, 3);
                        const sys = form.pressure_is_normal?.split('/')[0] || '120';
                        onChange({ target: { name: 'pressure_is_normal', value: `${sys}/${newVal}` } });
                      }}
                    />
                  </div>
                </div>

              </div>
            </>
          )}

          {error && (
            <div className="border border-codex-black bg-codex-panel px-4 py-3 text-sm">{error}</div>
          )}

          <button
            type="submit"
            className="mt-2 border border-codex-black bg-codex-black px-4 py-3 text-sm font-medium text-codex-white transition hover:bg-codex-white hover:text-codex-black"
          >
            {isRegister ? copy.auth.register : copy.auth.login}
          </button>
        </form>

        {/* Footer Links */}
        <div className="mt-6 text-sm text-codex-muted">
          {isRegister ? copy.auth.alreadyHave : copy.auth.needNew}{" "}
          <button
            type="button"
            onClick={onSwitchMode}
            className="border-b border-codex-black text-codex-black"
          >
            {isRegister ? copy.auth.loginInstead : copy.auth.registerInstead}
          </button>
        </div>

        {!isRegister && (
          <div className="mt-8 border-t border-codex-line pt-6 text-sm text-codex-muted">
            {copy.auth.demoAccess}: <span className="font-mono text-codex-black">nikola@codex.health</span> /{" "}
            <span className="font-mono text-codex-black">demo12345</span>
          </div>
        )}
      </div>
    </div>
  );
}
