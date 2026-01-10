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
        "n_cubits",
        type=int,
        help="Number of cubits used in the circuit, must be bigger than 0 and an integer"
    )
    return parser

def create_oracle(n_cubits: int) -> QuantumCircuit:
    circuit: QuantumCircuit = QuantumCircuit(n_cubits + 1)

    if np.random.randint(0, 2):
        circuit.x(n_cubits) # Aplica al bit auxiliar
    if np.random.randint(0, 2):
        return circuit
    
    # Si es balanceada
    on_states = np.random.choice(
        range(2**n_cubits),  # numbers to sample from
        2**n_cubits // 2,  # number of samples
        replace=False,  # makes sure states are only sampled once
    )

    for state in on_states:
        for qubit, bit in enumerate(reversed(bin(state)[2:])):
            if bit == "1":
                circuit.x(qubit)
        circuit.mcx(list(range(n_cubits)), n_cubits)
        for qubit, bit in enumerate(reversed(bin(state)[2:])):
            if bit == "1":
                circuit.x(qubit)
    
    return circuit

def run_circuit(circuit: QuantumCircuit) -> Any:
    simulator: AerSimulator = AerSimulator()
    compiled_circuit: QuantumCircuit = transpile(circuit, simulator)
    # Ejecutar, La distribución de todos los shots representa 
    # las probabilidades de cada estado, shot es una ejecucioón
    job: AerJob = simulator.run(compiled_circuit, shots=1)
    return job.result()

def is_constant(result: Any) -> bool: # true constant
    bits_string: str = list(result.get_counts().keys())[0]
    if '1' in bits_string:
        return False
    return True

def main() -> int:
    parser: argparse.ArgumentParser = create_Command_Line_Parser()
    arguments: argparse.Namespace = parser.parse_args()
    n_cubits: int = arguments.n_cubits # 0...n-1
    # Creamos el circuito con n + 1 y n bits clasicos para guardar la información 
    qc: QuantumCircuit = QuantumCircuit(n_cubits + 1, n_cubits) # Todos los cubits se inicializan a |0⟩

    # Aplicamos la puerta NOT a el bit auxiliar (n) y convertirlo a |1⟩
    qc.x(n_cubits)
    qc.barrier()

    # Aplicamos superposición a todos los cubits, el auxiliar pasa a ser |-⟩ para aprovechar 
    # el paralelismo con la devolución de fase
    qc.h(range(n_cubits + 1))
    qc.barrier()

    # Consultamos al oraculo Uf​∣x⟩∣y⟩=∣x⟩∣y⊕f(x)⟩ ----> C𝑋 |𝑐 𝑡⟩ = |𝑐 𝑡 ⊕ 𝑐⟩ | f(x)=0 | f(x)=1
    qc.compose(create_oracle(n_cubits), inplace=True)
    qc.barrier()
    
    # Aplicamos superposición de nuevo
    qc.h(range(n_cubits))
    qc.barrier()

    # Medimos los cubits salvo el ultimo que no hace falta
    qc.measure(range(n_cubits), range(n_cubits))
    
    print(qc.draw('text'))

    # Obtener resultados
    result = run_circuit(qc)
    counts = result.get_counts()

    print("Resultados de la medición:")
    print(counts)

    if is_constant(result):
        print('The function is constant')
    else:
        print('The function is balanced')

    return 0

if __name__ == '__main__':
    main()