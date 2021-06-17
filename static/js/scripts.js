// add recipe button
function createRecipeButton() {
    // shows recipe form
    $('#add-recipe-card').removeClass('hide');
    // hides add recipe button
    $('#create-recipe').addClass('hide');
}

// close button, closes recipe form
function hide() {
    $('#add-recipe-card').addClass('hide');
    $('#create-recipe').removeClass('hide');
}

// adds more steps to recipe form
function moreSteps() {
    $('.more-steps').removeClass('hide');
    $('.more-steps-button').toggle();
}