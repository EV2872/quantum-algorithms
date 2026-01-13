import argparse
from typing import Any
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator, AerJob
from qiskit import transpile

def create_Command_Line_Parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Quantum algorithm Deutsch-Jozsa",
        description="Generalization of the quantum algorithm Deutsch for N cubits",
        epilog="Example: python main.py n where n > 0"
    )
    # Argumento posicional obligatorio
    parser.add_argument(
        "n_qubits",
        type=int,
        help="Number of qubits used in the circuit, must be bigger than 0 and an integer"
    )
    return parser

def create_oracle(n_qubits: int) -> QuantumCircuit:
    circuit: QuantumCircuit = QuantumCircuit(n_qubits + 1)

    if np.random.randint(0, 2):
        circuit.x(n_qubits)
    if np.random.randint(0, 2):
        return circuit

    # Si es balanceada
    on_states = np.random.choice(
        range(2**n_qubits),
        2**n_qubits // 2, # nos quedamos con la mitad
        replace=False,
    )
    # f(x) = 1 solo para x ∈ {on_states}
    for state in on_states:
        little_endian_format: str = list(reversed(bin(state)[2:].zfill(n_qubits)))
        for qubit, bit in enumerate(little_endian_format):
            if bit == "1":
                circuit.x(qubit)
        circuit.mcx(list(range(n_qubits)), n_qubits)
        for qubit, bit in enumerate(little_endian_format):
            if bit == "1":
                circuit.x(qubit)

    return circuit

def run_circuit(circuit: QuantumCircuit) -> Any:
    simulator: AerSimulator = AerSimulator()
    compiled_circuit: QuantumCircuit = transpile(circuit, simulator)
    job: AerJob = simulator.run(compiled_circuit, shots=1)
    return job.result()

def is_constant(result: Any) -> bool: # true si es constante
    bits_string: str = list(result.get_counts().keys())[0]
    if '1' in bits_string:
        return False
    return True

def main() -> int:
    n_qubits: int = int(input('Introduce the number of qubits: ')) # 0...n-1
    print('\n')
    qc: QuantumCircuit = QuantumCircuit(n_qubits + 1, n_qubits) # Todos los cubits se inicializan a |0⟩ por defecto

    # Aplicamos la puerta NOT a el bit auxiliar (n) y convertirlo a |1⟩
    qc.x(n_qubits)
    qc.barrier()

    # Aplicamos superposición a todos los cubits, el auxiliar pasa a ser |-⟩ para aprovechar
    # el paralelismo con la devolución de fase
    qc.h(range(n_qubits + 1))
    qc.barrier()

    # Consultamos al oraculo Uf​∣x⟩∣y⟩=∣x⟩∣y⊕f(x)⟩ ----> C𝑋 |𝑐 𝑡⟩ = |𝑐 𝑡 ⊕ 𝑐⟩ | f(x)=0 | f(x)=1
    qc.compose(create_oracle(n_qubits), inplace=True)
    qc.barrier()

    # Aplicamos superposición de nuevo
    qc.h(range(n_qubits))
    qc.barrier()

    # Medimos los cubits salvo el ultimo que no hace falta
    qc.measure(range(n_qubits), range(n_qubits))

    print(qc.draw('text'))

    # Obtener resultados
    result = run_circuit(qc)
    counts = result.get_counts()

    print("Result of the measure:")
    print(counts)

    if is_constant(result):
        print('The function is constant')
    else:
        print('The function is balanced')

    return 0

if __name__ == '__main__':
    main()