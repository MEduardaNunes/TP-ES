import { useState } from 'react';

export default function Contador() {
  const [contador, setContador] = useState(0);

  return (
    <div className="contador">
      <div className="valor" data-cy="valor">
        {contador}
      </div>

      <button
        data-cy="botao-incrementar"
        onClick={() => setContador(contador + 1)}
      >
        + Incrementar
      </button>
    </div>
  );
}
