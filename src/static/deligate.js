const deligate = (result) => {
    if(result === false){
        window.location = '/register'
    }else{
        if(result['redirect']){
            window.location = result['redirect']
        }else{
            if(result['admin'] && result['admin'] == 1){
                window.location = '/admin';
            }else{
                window.location = '/done'
            }
        }
    }
}