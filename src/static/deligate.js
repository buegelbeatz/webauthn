const deligate = (result) => {
    if(result === false){
        window.location = '/'
    }else{
        if(result['redirect']){
            window.location = result['redirect']
        }else{
            if(result['admin'] && result['admin'] == 1){
                window.location = '/auth/admin';
            }else{
                window.location = '/done'
            }
        }
    }
}