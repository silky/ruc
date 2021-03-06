import numpy as np
from scipy.stats import unitary_group


def ruc_channel(ρ):
    """
    Quantum channel corresponding to fixed depth random
    unitary circuit.

    ρ is a numpy array of shape `[q,q,...q]` (`2*depth` times),
    where q is the local Hilbert space dimension.

    We assume `depth` row alternating with `depth` column indices: [r0, c0, r1, c1, ...]

    Returns: output density matrix of the same shape
    """

    shape = ρ.shape
    q = shape[0]
    depth = len(shape) // 2
    gates = random_gates(q, depth)

    # First trace out the first index
    ρ = np.trace(ρ, axis1=0, axis2=1)

    # We are going to 'a,h,...' for 'in' indices, `x,y,.... for 'out'
    # Capitals for contractions between unitaries
    # After contraction we move indices to the end using ellipsis notation
    # This will have the effect of reversing the ordering of the layers.

    ρ = np.einsum('aACx,bBCy,ab...->AB...xy', gates[0], gates[0].conj(), ρ)

    for gate in gates[1::-2]:
        ρ = np.einsum('aACx,bBDy,CDab...->AB...xy', gate, gate.conj(), ρ)

    ρ = np.einsum('Cx,Dy,CD...->...xy', gates[-1][0,0], gates[-1][0,0].conj(), ρ)

    # Return to original order of indices
    perm = np.arange(2*depth).reshape([-1,2])[::-1].reshape([2*depth])

    return ρ.transpose(perm)

def random_gates(q, depth):
    return [np.ascontiguousarray(unitary_group.rvs(q ** 2).reshape(4 * [q])) for _ in range(depth)]


def tensor_trace(tensor):
    """
    Calculate the matrix trace of a tensor with rows and column multi-indices as [r0, c0, r1, c1, ...]
    """
    while len(tensor.shape) != 0:
        tensor = np.einsum("aa...->...", tensor)

    return tensor


def tensor_conj_transp(tensor):
    """
    Calculate the conjugate transpose of a tensor with rows and column multi-indices as [r0, c0, r1, c1, ...]
    """
    tensor = tensor.conj()
    num_indices = len(tensor.shape)
    trans_perm = np.arange(num_indices).reshape([-1,2])[:,::-1].reshape([-1])
    tensor = tensor.transpose(trans_perm)

    return tensor


def trace_square(tensor):
    """
    Calculate the trace of the square of a tensor with rows and column multi-indices as [r0, c0, r1, c1, ...]
    """
    indices1 = "abcdefghijklmnopqrstuvwxyz"
    indices2 = "badcfehgjilknmporqtsvuxwzy"
    num_indices = len(tensor.shape)
    einsum_str = indices1[:num_indices] + "," + indices2[:num_indices] + "->"
    return np.einsum(einsum_str, tensor, tensor)