import argparse
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
    # Elegir tipo de oraculo
    parser.add_argument(
        "--oracle",
        choices=["constant0", "constant1", "balanced"],
        default="balanced",
        help="Oracle type"
    )
    return parser

def main() -> int:
    parser: argparse.ArgumentParser = create_Command_Line_Parser()
    arguments: argparse.Namespace = parser.parse_args()
    oracle_type: str = arguments.oracle
    n_cubits: int = arguments.n_cubits # 0...n-1
    aux_cubit_pos: int = n_cubits # ultima posición al cubit auxiliar
    # Creamos el circuito con n + 1 y n bits clasicos para guardar la información 
    qc: QuantumCircuit = QuantumCircuit(n_cubits + 1, n_cubits) # Todos los cubits se inicializan a |0⟩

    # Aplicar identidad a los cubits 0:n-1 salvo el auxiliar
    qc.id(range(n_cubits))

    # Aplicamos la puerta NOT a el bit auxiliar (n) y convertirlo a |1⟩
    qc.x(aux_cubit_pos)

    # Aplicamos superposición a todos los cubits, el auxiliar pasa a ser |-⟩ para aprovechar 
    # el paralelismo con la devolución de fase
    qc.h(range(n_cubits + 1))

    # Consultamos al oraculo Uf​∣x⟩∣y⟩=∣x⟩∣y⊕f(x)⟩ ----> C𝑋 |𝑐 𝑡⟩ = |𝑐 𝑡 ⊕ 𝑐⟩ | f(x)=0 | f(x)=1
    if oracle_type == "constant0":
        pass
    elif oracle_type == "constant1":
        qc.x(aux_cubit_pos)
    elif oracle_type == "balanced":
        for i in range(n_cubits):
            qc.cx(i, aux_cubit_pos)
    
    # Aplicamos superposición de nuevo
    qc.h(range(n_cubits))

    # Medimos los cubits salvo el ultimo que no hace falta
    qc.measure(range(n_cubits), range(n_cubits))
    
    print(qc.draw('text'))

    # Crear simulador
    simulator: AerSimulator = AerSimulator()

    # Transpilar el circuito para el simulador
    compiled_circuit: QuantumCircuit = transpile(qc, simulator)

    # Ejecutar, La distribución de todos los shots representa las probabilidades de cada estado, shot es una ejecucioón
    job: AerJob = simulator.run(compiled_circuit, shots=1024) 

    # Obtener resultados
    result = job.result()
    counts = result.get_counts()

    print("Resultados de la medición:")
    print(counts)

    return 0

if __name__ == '__main__':
    main()