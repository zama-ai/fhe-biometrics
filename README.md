# FHE Biometrics
# TFHE-UBIRIS

[An OnlyDust project](https://app.onlydust.xyz/projects/f0d669e2-a45f-44ca-ae32-7b3d69ee12ba)

## Homomorphic Biometrics: ID verification

### General description

Biometric recognition is becoming a prominent way to authenticate users or verify their identities. As highlighted in the ISO/IEC 24745, it is important to protect biometric information for secrecy, irreversibility, and renewability during storage and transfer. In this bounty you will need to design an FHE based remote authentication system that protects sensitive Iris information during storage and biometric comparison. In its paper "Hybrid biometric template protection: Resolving the agony of choice between bloom filters and homomorphic encryption", the research team looked at three different approaches: Bloom filters, homomorphic encryption and hybrid biometric template protection (BTP). The team highlighted the advantages and disadvantages of each approach.

### Objective

The bounty objective is to:
- use Zama libraries to implement a single key TFHE-based BTP for an access control system
- all reference templates are stored encrypted in a database on the server

### Implementation

The client:
- collects the iris biometric (format should be the same as UBIRIS.v2)
- extracts the feature vector
- encrypt it
- and send it to the server

Then the server:
- perform the comparison against its database
- send an encrypted matching ID back to client
- a no match encrypted message is returned if no matching template is found
- the system will need to have an Equal Error Rate (EER) of 0.1%
- the UBIRIS.V2 database will be used to compute the error rates
