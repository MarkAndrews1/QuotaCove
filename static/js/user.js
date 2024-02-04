async function toggleFollow(){

    let id = $(this).attr('id')
    let $btn = $(this)
    res = await axios.post(`/users/follow/${id}`)

    if(res.data === 'Followed'){
        $btn.attr('class', 'btn btn-sm btn-outline-secondary')
        $btn.text('Unfollow')
    }else{
        $btn.attr('class', 'btn btn-sm btn-outline-primary')
        $btn.text('Follow')
    }
}
    
$("[name='follow-btn']").on('click', toggleFollow)


async function showFollowers(id) {
    try {
        const res = await axios.get(`/users/${id}/data`, { params: { type: 'followers' } });
        const followers = res.data;

        if (followers.length === 0) {
            const mainDiv = $("#profile-main-content");
            mainDiv.html('<h3>Looks like no one is here. . . </h3>');
        } else {
            const userElements = followers.map(user => `
            <div class="column">
            <h3>Followers</h3>
            <hr>
            <div class="profile-div">
            <a href="/users/${user.id}" class="profile-avatar">
                <img src="${user.img_url}" alt="user image" class="profile-avatar">
            </a>
            <a href="/users/${user.id}"><h3>@${user.username}</h3></a>
            <p class="fav-quote">${user.fav_quote} -<small><i>${user.fav_quote_author}</i></small></p>
            </div>
            </div>
            `);

            $("#profile-card-title").html('Followers')
            const mainDiv = $("#profile-main-content");
            mainDiv.html(userElements.join(''));
        }
    } catch (error) {
        console.error('Error fetching followers:', error);
    }
}

$("[name='followers-btn']").on('click', function() {
    const id = $(this).attr('id');
    showFollowers(id);
});


async function showFollowing(id) {
    try {
        const res = await axios.get(`/users/${id}/data`, { params: { type: 'following' } });
        const following = res.data;

        if (following.length === 0) {
            const mainDiv = $("#profile-main-content");
            mainDiv.html('<h3>Looks like no one is here. . . </h3>');
        } else {
            const userElements = following.map(user => `
            <div class="column">
            <h3>Following</h3>
            <hr>
            <div class="profile-div">
            <a href="/users/${user.id}" class="profile-avatar">
                <img src="${user.img_url}" alt="user image" class="profile-avatar">
            </a>
            <a href="/users/${user.id}"><h3>@${user.username}</h3></a>
            <p class="fav-quote">${user.fav_quote} -<small><i>${user.fav_quote_author}</i></small></p>
            </div>
            </div>`);

            $("#profile-card-title").html('Following')
            const mainDiv = $("#profile-main-content");
            mainDiv.html(userElements.join(''));
        }
    } catch (error) {
        console.error('Error fetching following:', error);
    }
}

$("[name='following-btn']").on('click', function() {
    const id = $(this).attr('id');
    showFollowing(id);
});
