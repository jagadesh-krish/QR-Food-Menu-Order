const decrementButtons = document.querySelectorAll('.decrement');
const incrementButtons = document.querySelectorAll('.increment');

    decrementButtons.forEach(button => {
        button.addEventListener('click', () => {
            const target = button.dataset.target;
            const input = document.querySelector(`input[name="${target}"]`);
            if (input.value > 0) {
                input.value--;
                button.nextElementSibling.disabled = false;
            }
        });
    });

    incrementButtons.forEach(button => {
        button.addEventListener('click', () => {
            const target = button.dataset.target;
            const input = document.querySelector(`input[name="${target}"]`);
            input.value++;
            button.previousElementSibling.disabled = false;
        });
    });

    document.querySelector('form').addEventListener('submit', function(event) {
        event.preventDefault();
        const mobileNum = document.querySelector('input[name="mobile_no"]').value;
        const regex = /^(?:(?:\+|0{0,2})91(\s*|[\-])?|[0]?)?([6789]\d{2}([ -]?)\d{3}([ -]?)\d{4})$/;
        if (!regex.test(mobileNum)) {
            alert("Not a valid mobile number!");
        } else {
            this.submit();
        }
    });
    