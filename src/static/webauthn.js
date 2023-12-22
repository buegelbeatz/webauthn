// Webauthn

const _asBase64 = ab => btoa(String.fromCharCode(...new Uint8Array(ab)))

const _callWebAuthn = async (title, path, body)  => {
    try {
        const response = await fetch(path, {
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' }, 
            body: (body)?JSON.stringify(body):null
        });
        return JSON.parse(await response.json());
    } catch (error) {
        console.error('Error during '+title+':', error);
        throw new Error('Error during '+title);
    }
}

const _finalize = async (title, path, credential) => {
    result = await _callWebAuthn(title,path,{credential: credential});
    return (result['verified'] == 1)?result:false;
}

const _public_key = (challenge, timeout) => ({challenge: Uint8Array.from(challenge, c => c.charCodeAt(0)), timeout: timeout})

const _credentials = (id,clientDataJSON,signature,authenticatorData, attestationObject, userHandle) => {
    const cred = { id: id, rawId: id, response: { clientDataJSON: _asBase64(clientDataJSON) } }
    signature && (cred.response.signature = _asBase64(signature));
    authenticatorData && (cred.response.authenticatorData = _asBase64(authenticatorData));
    attestationObject && (cred.response.attestationObject = _asBase64(attestationObject));
    userHandle && (cred.response.userHandle = _asBase64(userHandle));
    return cred;
}

async function registerWebAuthn(id) {
    try {
        const data = await _callWebAuthn('Registration','/register/challenge',{id});
        console.log('registerWebAuthn.challenge', data)
        data.user.id = Uint8Array.from(data.user.id, c => c.charCodeAt(0));
        const publicKey = _public_key(data.challenge, data.timeout)
        publicKey['rp'] = data.rp;
        publicKey['user'] = data.user;
        publicKey['pubKeyCredParams'] = data.pubKeyCredParams;
        publicKey['attestation'] = data.attestation;
        const credential = await navigator.credentials.create({ publicKey });
        const {attestationObject, clientDataJSON} = credential.response
        const credential_send = _credentials(credential.id, clientDataJSON, null, null, attestationObject, null);
        credential_send['user'] = data['user']['name'];
        console.log('registerWebAuthn.create', credential_send)
        return await _finalize('Finalize registration','/register/finalize',credential_send);
    } catch (error) {
        console.error('Error during registration:', error);
    }
    return false;
}

async function loginWebAuthn() {
    try {
        const data = await _callWebAuthn('Login','/login/challenge',null);
        console.log('loginWebAuthn.challenge', data)
        const publicKey = _public_key(data.challenge, data.timeout)
        console.log('publicKey', publicKey)
        const credential = await navigator.credentials.get({ publicKey });
        const {authenticatorData, signature, userHandle, clientDataJSON} = credential.response
        const credential_send = _credentials(credential.id, clientDataJSON, signature, authenticatorData, null, userHandle);
        console.log('loginWebAuthn.get', credential_send, data.challenge)
        return await _finalize('Finalize login','/login/finalize',credential_send, data.challenge);
    } catch (error) {
        console.error('Error during login:', error);
    }
    return false;
}