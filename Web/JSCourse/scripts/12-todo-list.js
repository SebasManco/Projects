const list = [{
    name: 'hola',
    dueDate: '12/22/2023'
},
{
    name: 'adios',
    dueDate: '11/22/2024'    
}];
renderToDoList(); 

function renderToDoList(){
    let toDoListHTML = '';

    list.forEach(function(toDoObject,index) {
        const { name, dueDate } = toDoObject;
        const html = `
        <div>${name}</div>
        <div>${dueDate}</div>
        <button onclick="
            list.splice(${index},1);
            renderToDoList();
        " class="delete-todo-button">delete</button>\n`;
        toDoListHTML += html;
    });
    
    console.log(toDoListHTML)
    
    document.querySelector('.js-todo-list')
        .innerHTML = toDoListHTML; 
}

function addToDo(){
    const inputElement = document.querySelector('.js-name-input');
    const name = inputElement.value;
    const dateInputElement = document.querySelector('.js-due-date-input')
    const dueDate = dateInputElement.value;

    console.log(dueDate)

    list.push({
        name,
        dueDate
    })
    console.log(list);

    inputElement.value = '';
    renderToDoList()
}