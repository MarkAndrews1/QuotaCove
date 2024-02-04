
async function toggleSave() {
    let id = $(this).attr('id');
    let $heart = $(this).find('#heart');

    try {
        const response = await axios.post(`/quotes/save/${id}`);
        const status = response.data.status;

        // Update the heart icon based on the status
        if (status === 'save') {
            $heart.attr('class', 'fa-solid fa-heart');
        } else if (status === 'unsave') {
            $heart.attr('class', 'fa-regular fa-heart');
        }

    } catch (error) {
        console.error('Error:', error);
        // Handle the error, e.g., show a message to the user
    }
}

$("[name='save-btn']").on('click', toggleSave);


async function deleteQuote() {
    let id = $(this).attr('id');
    let li = $(this).closest('li');

    try {
        let res = await axios.post(`/quotes/delete/${id}`);

        if (res.status === 200) {
            li.remove();
        } else {
            console.log('Failed Deletion. Status:', res.status);
        }
    } catch (error) {
        console.error('Error deleting quote:', error);
    }
}

$("[name='delete-btn']").on('click', deleteQuote)

