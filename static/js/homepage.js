async function getUsers(evt) {
    evt.preventDefault();

    let searchTerm = $(this).find('input').val();

    try {
        const res = await axios.get('/users', { params: { search: searchTerm } });
        const users = res.data;

        $(this).find('input').val('');

        if (users.length === 0) {
            const mainDiv = $("#main-content-area");
            mainDiv.html(`<h3>Sorry, we couldn\'t find anyone.</h3>`);

        } else {
            const userElements = users.map(user => `<div class="profile-div">
                <a href="/users/${user.id}" class="profile-avatar">
                    <img src="${user.img_url}" alt="user image" class="profile-avatar">
                </a>
                <a href="/users/${user.id}"><h3>@${user.username}</h3></a>
                <p class="fav-quote">${user.fav_quote} -<small><i>${user.fav_quote_author}</i></small></p>
            </div>`);

            const mainDiv = $("#main-content-area");
            mainDiv.html(userElements.join(''));
        }

    } catch (error) {
        console.error('Error fetching users:', error);
    }
}

$("#search-form").on('submit', getUsers);



async function getTags(){

    try {
        const res = await axios.get('/tags')
        const tags = res.data
        console.log(tags)

        const tagElements = tags.map(tag => `<a href="/tags/${tag.id}"><h4>${tag.name}:</h4></a>`);

    const mainDiv = $("#main-content-area");
    mainDiv.html(tagElements.join(''));

    }catch (error) {
        console.error('Error fetching tags:', error);
    }
}

$('#tags-btn').on('click', getTags)

