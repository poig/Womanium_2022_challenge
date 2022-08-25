## Digital-analog Variational Quantum Eigensolver
### problem statement: designing analog VQE ansatz for H2 problem, but I didn't go too deep into it, just run some of the results to discuss.

### my solution: method from IBM research paper, focusing on Analog quantum computing, and design to be hardware efficient, 
in which the hardware is a superconducting computer, 

### implementation & scaling: 

#### there is two different way to think about quantum simulation:
- Analog quantum simulation is a way to think about quantum simulation, in which we are emulating the system by recreating the hamiltonian of the system want to simulate
tunable parameters, so we can study various regimes, for a more controllable system. 

- Digital quantum simulation is another way to think about quantum simulation, but limited by the native interactions of the simulator, 
where evolution is decomposed in elementary gates, so can achieve any quantum evolution, for example, trotterization method.  

#### what is GaussianSquare
- A square pulse with a Gaussian shaped risefall on both sides lifted such that its first sample is zero.

- RZX gate is The cross-resonance gate (CR) for superconducting qubits implements a ZX interaction

- The RZXCalibrationBuilderNoEcho is a creates calibrations for the cross-resonance pulses without inserting the echo pulses in the pulse schedule. 
This enables exposing the echo in the cross-resonance sequence as gates so that the transpiler can simplify them. 
The RZXCalibrationBuilderNoEcho only supports the hardware-native direction of the CX gate. 

- which just make the entanglement and skip the extra rotation, which generate cnot.