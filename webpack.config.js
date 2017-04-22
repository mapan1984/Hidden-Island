var path = require('path')
var webpack = require('webpack')

module.exports = {             // __dirname 指webpack.config.js所在目录
  devtool: 'eval-source-map',  // 配置生成Source Maps

  entry: path.resolve(__dirname, 'app/static/component/blog.jsx'),  // 唯一打包入口文件
  output: {
    path: path.resolve(__dirname, 'app/static/scripts'),  // 打包后文件存放的地方
    filename: 'bundle.js'                  // 打包后输出文件的文件名
  },

  module: {
    loaders: [
      {
        test: /\.jsx?$/,  // 匹配loaders所处理文件的扩展名的正则表达式(必须)
        exclude: /node_modules/,  // 不需要打包的文件夹(可选)
        loader: 'babel-loader',  // loader的名称(必须)
        query: {  // 为loaders提供的额外的设置选项(可选)，也可在项目目录下使用.babelrc进行配置
          presets: ['es2015', 'react']
        }
      }
    ]
  }
}
