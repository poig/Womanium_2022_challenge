# We will need some functionality 
import os
from typing import List 

# and from math related libraries
#import qutip as qt
import numpy as np
from numbers import Number
import pylab
from IPython.display import display, clear_output

# and from qiskit
from qiskit.extensions import HamiltonianGate
from qiskit import QuantumCircuit, QuantumRegister, Aer, execute, IBMQ, transpile, schedule as build_schedule
from qiskit.providers.aer import QasmSimulator, StatevectorSimulator
from qiskit.quantum_info import Operator
from qiskit.utils import QuantumInstance, algorithm_globals
from qiskit.utils.mitigation import CompleteMeasFitter
from qiskit.algorithms import VQE, NumPyMinimumEigensolver
from qiskit.algorithms.optimizers import COBYLA, L_BFGS_B, SPSA, SLSQP
from qiskit.circuit import Gate, ParameterExpression, Parameter, ParameterVector

from qiskit.quantum_info.operators.predicates import matrix_equal, is_hermitian_matrix
from qiskit.extensions.exceptions import ExtensionError
from qiskit.circuit.exceptions import CircuitError
from qiskit.extensions.unitary import UnitaryGate
from qiskit.circuit.library import TwoLocal
from qiskit.opflow import I, X, Z
from qiskit.providers.aer.noise import NoiseModel
from qiskit.visualization import plot_gate_map, plot_error_map, plot_circuit_layout, plot_coupling_map

from qiskit.transpiler import PassManager
from qiskit.transpiler.passes.calibration import RZXCalibrationBuilderNoEcho
from qiskit_nature.algorithms import GroundStateEigensolver, NumPyMinimumEigensolverFactory, VQEUCCFactory
from qiskit_nature.drivers import Molecule
from qiskit_nature.drivers.second_quantization import ElectronicStructureDriverType, ElectronicStructureMoleculeDriver
from qiskit_nature.problems.second_quantization import ElectronicStructureProblem
from qiskit_nature.converters.second_quantization import QubitConverter
from qiskit_nature.transformers.second_quantization.electronic import FreezeCoreTransformer
from qiskit_nature.operators.second_quantization import FermionicOp
from qiskit_nature.mappers.second_quantization import ParityMapper
import matplotlib.pyplot as plt

from qiskit_nature import settings
settings.dict_aux_operators = False


seed = 170
iterations = 20
algorithm_globals.random_seed = seed

class iteration_callback():
    """return iteration data
        """
    def __init__(self):
        self.counts = []
        self.values = []
        self.params = []
        self.deviation = []
        
    def store_intermediate_result(self, eval_count, parameters, mean, std):
        display("Evaluation: {}, Energy: {}, Std: {}".format(eval_count, mean, std))
        clear_output(wait=True)
        self.counts.append(eval_count)
        self.values.append(mean)
        self.params.append(parameters)
        self.deviation.append(std)
    
    def get_count(self):
        return self.counts

    def get_value(self):
        return self.values
    

def run_vqe(operator, name, ansatz, qi, parameters = None,optimizer=SPSA(maxiter=iterations), construct = False, output= True):
    """
    Args:
        operator: problem
        ansatz: ansatz circuit
        qi: QI backends
        optimizer: optimizer
        construct(bool): print circuit
        output(bool): calculate and print output
    Return:
        iter_result: dictionary of iter_result
        result: dictionary of result
    """
    iter_result = iteration_callback()
    vqe = VQE(ansatz, optimizer=optimizer, callback=iter_result.store_intermediate_result, quantum_instance=qi)
    if construct:
        if parameters == None:
            parameters = ansatz.parameters 
        circuits = vqe.construct_circuit(parameters,operator)
        for i,circuit in enumerate(circuits):
            print('circuit{}:\n'.format(i))
            display(circuit.decompose(reps=2).draw('mpl'))
    if output:
        result = vqe.compute_minimum_eigenvalue(operator=operator)
        return iter_result, result

def print_result(name, iter_result_,result_, qi,ref_value):
    """print out result from run_all_vqe()

        Args:
            name: list of ansatz name
            iter_result: dictionary of iter_result
            result: dictionary of result
            qi: list of backend
            ref_value: reference value
        """
    for i in range(len(name)):
        iter_result,result = iter_result_[f'iter{i}'], result_[f'result{i}']
        for j,(iter_result,result) in enumerate(zip(iter_result,result)):
            backend = str(qi[j].backend)
            
            if bool(qi[j].noise_config) and qi[j]._meas_error_mitigation_cls is None: #if have noise but no mit
                pylab.plot(iter_result.get_count(), iter_result.get_value(),label="noise")
                print(f'{name[i]} on {backend} (noise): {result.eigenvalue.real:.5f} ({(result.eigenvalue.real - ref_value):.5f})')
                
            elif bool(qi[j].noise_config) and not(qi[j]._meas_error_mitigation_cls is None): #if have noise and mit
                pylab.plot(iter_result.get_count(), iter_result.get_value(),label="noise and measurement error mitigation")
                print(f'{name[i]} on {backend} (noise and measurement error mitigation): {result.eigenvalue.real:.5f} ({(result.eigenvalue.real - ref_value):.5f})')
                
            else:
                pylab.plot(iter_result.get_count(), iter_result.get_value(),label="no noise")
                print(f'{name[i]} on {backend} (no noise): {result.eigenvalue.real:.5f} ({(result.eigenvalue.real - ref_value):.5f})')
        pylab.rcParams['figure.figsize'] = (12, 4)
        pylab.xlabel('Eval count')
        pylab.ylabel('Energy')
        pylab.title(f'Convergence with three different condition on ansatz{i}')
        pylab.axhline(y=ref_value,linestyle="--")
        pylab.legend()
        pylab.show()

def run_all_vqe(operator, ref_value, name, ansatz, qi ,optimizer=SPSA(maxiter=iterations)):
    """loop ansatz through list of backends

        Args:
            operator: problem
            name: list of ansatz name
            ansatz: list of ansatz
            qi: list of backend
            optimizer: optimizer
        Return:
            all_iter_result: dictionary of iter_result
            all_result: dictionary of result
        """
    all_iter_result = {}
    all_result = {}
    for i in range(len(ansatz)):
        iter_list = []
        result_list = []
        for j in range(len(qi)):
            backend = str(qi[j].backend)
            
            if bool(qi[j].noise_config) and qi[j]._meas_error_mitigation_cls is None: #if have noise but no mit
                iter_result, result = run_vqe(operator,f"{name[i]} on {backend} (noise)", ansatz[i], qi[j], optimizer)
                
            elif bool(qi[j].noise_config) and not(qi[j]._meas_error_mitigation_cls is None): #if have noise and mit
                iter_result, result = run_vqe(operator,f"{name[i]} on {backend} (noise and measurement error mitigation)", ansatz[i], qi[j], optimizer)
                
            else:
                iter_result, result = run_vqe(operator,f"{name[i]} on {backend} (no noise)", ansatz[i], qi[j],optimizer)
                
                
                
            iter_list.append(iter_result)
            result_list.append(result)
        
        all_iter_result[f"iter{i}"]= iter_list
        all_result[f"result{i}"] = result_list
    print_result(name, all_iter_result, all_result, qi,ref_value)
    return all_iter_result, all_result

def run_energy(vqe_circuit, total_dist=4, dist=0.1, incr_early=0.1, incr_late=0.3):
    """loop through the energy, and print result.

        Args:
            total_dist: total length
            dist: starting point
            incr_early: increase point in first half
            incr_late: increase point in second half
        """
    
    real_energies = []
    vqe_energies = []
    dists = []
    qubit_converter = QubitConverter(ParityMapper(), two_qubit_reduction=True)
    print(dist, total_dist)
     
    while dist < total_dist:
        molecule = Molecule(geometry=[['H', [0., 0., 0.]], ['H', [0., 0., dist]]])
        driver = ElectronicStructureMoleculeDriver(molecule, basis='sto3g', \
        driver_type=ElectronicStructureDriverType.PYSCF)
        
        numpy_solver = NumPyMinimumEigensolver()
        es_problem = ElectronicStructureProblem(driver)
        second_q_ops = es_problem.second_q_ops()   
        if dist == 0.1:
            FermionicOp.set_truncation(0)
            second_q_ops = second_q_ops
            FermionicOp.set_truncation(1)
            qubit_op = qubit_converter.convert(second_q_ops[0], num_particles=es_problem.num_particles)
            es_problem_ = es_problem.grouped_property
    
        calc = GroundStateEigensolver(qubit_converter, numpy_solver)
        res = calc.solve(es_problem)
        real_energies.append(np.real(res.total_energies[0]))
        #H2_op = qubit_converter.convert(second_q_ops[0], num_particles=es_problem.num_particles)
        
        #result = numpy_solver.compute_minimum_eigenvalue(operator=H2_op)
        #ref_value = result.eigenvalue.real
        #real_energies.append(ref_value)
        #display(print(f'Reference value: {ref_value:.5f}'))
    
        calc = GroundStateEigensolver(qubit_converter, vqe_circuit)
        res = calc.solve(es_problem)
        vqe_energies.append(np.real(res.total_energies[0]))
        
        #result = vqe_circuit.compute_minimum_eigenvalue(operator=H2_op)
        #vqe_energies.append(result.eigenvalue.real)
        #print(f'{dist}: {result.eigenvalue.real:.5f} ({(result.eigenvalue.real - ref_value):.5f})')
        
        
        dists.append(dist)
        if dist > total_dist / 2:
            dist += incr_late
        else:
            dist += incr_early
    
    plt.plot(dists, real_energies, label='Real', color='red')
    plt.scatter(dists, vqe_energies, label='VQE', color='black')
    plt.title("H2")
    plt.ylim(-1.2, 0.4)
    plt.xlim(0, 4)
    plt.xlabel('Angstroms')
    plt.ylabel('Hartree')
    plt.legend()
    plt.show()
    return dists,real_energies, vqe_energies, second_q_ops, qubit_op, es_problem_


    
def HEA_aware(num_q, depth, hardware):
    circuit = QuantumCircuit(num_q)
    params = ParameterVector("theta", length=num_q * (3 * depth + 2))
    counter = 0
    inst_map = hardware.defaults().instruction_schedule_map
    channel_map = hardware.configuration().qubit_channel_mapping
    for q in range(num_q):
        circuit.rx(params[counter], q)
        counter += 1 
        circuit.rz(params[counter], q)
        counter += 1
    for d in range(depth):
        circuit.barrier()
        for q in range(num_q - 1):
            gate = QuantumCircuit(num_q)
            gate.rzx(np.pi/2, q, q + 1)
            pass_ = RZXCalibrationBuilderNoEcho( instruction_schedule_map=inst_map,qubit_channel_mapping=channel_map,)
            #Creates calibrations for RZXGate(theta) by stretching and compressing Gaussian square pulses in the CX gate.
            qc_cr = PassManager(pass_).run(gate)
            circuit.compose(qc_cr, inplace=True)
        circuit.barrier()
        for q in range(num_q):
            circuit.rz(params[counter], q)
            counter += 1
            circuit.rx(params[counter], q)
            counter += 1 
            circuit.rz(params[counter], q)
            counter += 1
    return circuit, params


def HEA_naive(num_q, depth):
    circuit = QuantumCircuit(num_q)
    params = ParameterVector("theta", length=num_q * (3 * depth + 2))
    counter = 0
    for q in range(num_q):
        circuit.rx(params[counter], q)
        counter += 1 
        circuit.rz(params[counter], q)
        counter += 1
    for d in range(depth):
        for q in range(num_q - 1):
            circuit.cx(q, q + 1)
        for q in range(num_q):
            circuit.rz(params[counter], q)
            counter += 1
            circuit.rx(params[counter], q)
            counter += 1 
            circuit.rz(params[counter], q)
            counter += 1
    return circuit, params